from typing import List, Optional, Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# ВАЖНО: путь импорта ConsultantCore зависит от структуры проекта.
# Если этот файл лежит в backend/routers/ai.py и пакет backend настроен, 
# то вариант ниже подойдёт.
try:
    # вариант, когда запускаем как пакет backend.*
    from backend.ai.core import ConsultantCore  # type: ignore
except ImportError:
    # вариант, когда используем относительный импорт из backend/routers/
    from ..ai.core import ConsultantCore  # type: ignore


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


class Citation(BaseModel):
    """Ссылка на закон / нормативный акт, на который ссылается ответ."""
    id: str = Field(..., description="Краткое обозначение нормы: ст. 10 ГК РФ и т.п.")
    title: Optional[str] = Field(
        None, description="Название закона или краткое описание нормы."
    )
    url: Optional[str] = Field(
        None, description="Необязательная ссылка на текст закона в интернете."
    )


class AIAskRequest(BaseModel):
    """
    Запрос к ЮИИ Татьяне из чата.

    - query: сам вопрос пользователя
    - country: страна законодательства (RU/BY/UA/EU)
    - category: направление права (civil/criminal/housing/family/migration)
    - mode: режим (пока просто 'dialog', на будущее)
    """
    query: str = Field(..., min_length=3, description="Вопрос или описание ситуации.")
    country: Optional[str] = Field(
        None,
        description="Код страны: RU, BY, UA, EU.",
    )
    category: Optional[str] = Field(
        None,
        description="Направление права.",
    )
    mode: Optional[str] = Field(
        "dialog",
        description="Режим работы (на будущее: dialog, draft_document и т.п.).",
    )


class AIAskResponse(BaseModel):
    """
    Ответ ЮИИ Татьяны.

    - answer: текст ответа (уже человечный, с объяснениями и структурой)
    - citations: список ссылок на законы
    """
    answer: str
    citations: List[Citation] = Field(default_factory=list)


def _human_country(country: Optional[str]) -> str:
    if country == "RU":
        return "Российской Федерации"
    if country == "BY":
        return "Республики Беларусь"
    if country == "UA":
        return "Украины"
    if country == "EU":
        return "Европейского Союза"
    return "выбранной юрисдикции"


def _human_category(category: Optional[str]) -> str:
    mapping = {
        "civil": "гражданское право",
        "criminal": "уголовное право",
        "housing": "жилищные отношения",
        "family": "семейное право",
        "migration": "миграционные вопросы",
    }
    return mapping.get(category or "", "соответствующую отрасль права")


# Инициализируем Татьяну (ConsultantCore) один раз при загрузке модуля
consultant = ConsultantCore()


@router.post("/ask", response_model=AIAskResponse)
async def ask_ai(request: AIAskRequest) -> AIAskResponse:
    """
    Основной endpoint для чата с ЮИИ Татьяной.

    ВМЕСТО "умной заглушки" теперь:
    - формируем расширенный запрос с учётом страны и категории,
    - передаём его в ConsultantCore (Татьяна),
    - возвращаем её ответ и реальные ссылки (citations), которые даёт RAG/AI.
    """
    query = (request.query or "").strip()
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Слишком короткий запрос.")

    # Человеческое описание страны и отрасли для контекста
    country_h = _human_country(request.country)
    category_h = _human_category(request.category)

    # Расширяем запрос контекстом (чтобы Татьяна учитывала юрисдикцию/отрасль)
    # Здесь мы НЕ подменяем вопрос, а добавляем указание контекста.
    enriched_query_parts: List[str] = []

    if request.country:
        enriched_query_parts.append(f"[Юрисдикция: {request.country} ({country_h})]")
    if request.category:
        enriched_query_parts.append(f"[Отрасль: {request.category} ({category_h})]")
    if request.mode:
        enriched_query_parts.append(f"[Режим: {request.mode}]")

    enriched_query_parts.append(query)
    enriched_query = " ".join(enriched_query_parts)

    try:
        # Вызов ядра консультанта Татьяны
        result: Dict[str, Any] = await consultant.ask(enriched_query)
    except ValueError as e:
        # Любые "честные" ошибки от Татьяны переводим в 400
        raise HTTPException(status_code=400, detail=str(e))

    # Ожидаем, что Татьяна возвращает словарь с ключами:
    # - answer: str
    # - citations: List[Dict] или похожую структуру с id/title/url
    raw_answer = result.get("answer") or ""
    raw_citations = result.get("citations") or []

    # Переводим цитаты в нашу Pydantic-модель Citation
    citations: List[Citation] = []
    for item in raw_citations:
        # item может быть dict или объект; работаем по-минимуму через dict-интерфейс
        if isinstance(item, dict):
            cid = str(item.get("id") or "").strip()
            if not cid:
                # пропускаем странные записи без id
                continue
            citations.append(
                Citation(
                    id=cid,
                    title=item.get("title"),
                    url=item.get("url"),
                )
            )
        else:
            # На всякий случай, если что-то иное — приводим к строке
            cid = str(getattr(item, "id", "") or "").strip()
            if cid:
                citations.append(
                    Citation(
                        id=cid,
                        title=getattr(item, "title", None),
                        url=getattr(item, "url", None),
                    )
                )

    # Если по какой-то причине answer пустой — подстрахуемся понятным сообщением
    if not raw_answer:
        raw_answer = (
            "У меня не получилось сформировать развернутый ответ на ваш запрос. "
            "Попробуйте переформулировать вопрос или добавить больше деталей. "
            "Также вы можете обратиться к живому юристу, особенно если ситуация срочная или рискованная."
        )

    return AIAskResponse(answer=raw_answer, citations=citations)
