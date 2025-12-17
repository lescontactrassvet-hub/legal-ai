from typing import Optional, List
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

# Ядро ИИ-юриста Татьяны (по структуре проекта оно лежит в backend/ai/core.py)
from ai.core import ConsultantCore
from ai.nlp.rubert_intent import classify_intent

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)

MAX_QUESTION_LEN = 4000

# Инициализируем ядро Татьяны один раз.
# Внутри ConsultantCore → LocalGenerator, который сам решает:
# - использовать GigaChat (если заданы ключи);
# - или работать в локальном режиме (fallback).
consultant_core = ConsultantCore()


class ChatRequest(BaseModel):
    """Запрос к ИИ-консультанту Татьяне.

    Фронтенд может отправлять текст либо в поле message, либо в question.
    Мы поддерживаем оба варианта, чтобы не ломать разные версии UI.
    """

    message: Optional[str] = Field(
        None, description="Текст вопроса пользователя (основное поле)"
    )
    question: Optional[str] = Field(
        None, description="Альтернативное поле для текста (для старых фронтов)"
    )
    language: Optional[str] = Field(
        None, description="Желаемый язык ответа: ru / en и т.п."
    )

    def normalized_text(self) -> str:
        """Берём текст из message или question и приводим к нормальной строке."""
        text = (self.message or self.question or "").strip()
        return text


class Citation(BaseModel):
    """Ссылка на норму права / документ."""

    id: str = Field(
        ...,
        description=(
            "Краткое обозначение нормы: ст. 10 ГК РФ, Постановление "
            "Правительства № ... и т.п."
        ),
    )
    title: Optional[str] = Field(
        None, description="Полное название закона или документа"
    )
    url: Optional[HttpUrl] = Field(
        None, description="Ссылка на официальный текст (консультант/Гарант/Госправо)"
    )


class AiResponse(BaseModel):
    """Ответ ИИ-консультанта для фронтенда dashboard.html."""

    answer: str = Field(..., description="Текст ответа Татьяны")
    citations: List[Citation] = Field(
        default_factory=list,
        description="Список найденных норм права (пока может быть пустым)",
    )
    document_draft: Optional[str] = Field(
        None,
        description=(
            "Черновик документа, если удалось его сформировать. "
            "Фронтенд кладёт это поле в редактор под чатом."
        ),
    )


@router.post("/ask", response_model=AiResponse)
async def ask_ai(payload: ChatRequest) -> AiResponse:
    """
    Главный эндпоинт чата Татьяны.

    Теперь это тонкий слой над ConsultantCore:
    - принимает текст вопроса;
    - проверяет, что текст не пустой и не слишком длинный;
    - передаёт запрос в ядро ИИ-юриста Татьяны (ConsultantCore);
    - возвращает структурированный ответ для фронтенда.
    """
    text = payload.normalized_text()
    if not text:
        raise HTTPException(status_code=400, detail="Пустой запрос")

    # Защита от слишком длинных запросов — не даём «убить» бэкенд
    if len(text) > MAX_QUESTION_LEN:
        text = text[:MAX_QUESTION_LEN]
    # --- NLP слой (RuBERT / fallback) ---
    nlp_info = classify_intent(text)
    logger.info(
        "NLP intent=%s confidence=%.2f engine=%s",
        nlp_info.get("intent"),
        nlp_info.get("confidence", 0.0),
        nlp_info.get("engine"),
    )
    # -----------------------------------

    try:
        # Вызов ядра Татьяны.
        # ConsultantCore.ask возвращает dict вроде:
        # {"answer": str, "citations": [...], "intent": ..., "risk_info": ...}
        core_result = await consultant_core.ask(text)
    except ValueError as exc:
        # Ядро может вернуть ValueError для пустых/некорректных запросов
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        # Логируем внутрь, но не раскрываем детали наружу — безопасность.
        logger.exception("Ошибка при обработке запроса Татьяной: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=(
                "Сервис ИИ-консультанта Татьяны временно недоступен. "
                "Повторите попытку позже."
            ),
        )

    # Если ядро вернуло не словарь — спасаем ситуацию, приводим к строке.
    if not isinstance(core_result, dict):
        answer_text = str(core_result)
        return AiResponse(
            answer=answer_text,
            citations=[],
            document_draft=None,
        )

    # Основной текст ответа
    answer_text = core_result.get("answer")
    if not isinstance(answer_text, str):
        answer_text = (
            "Извините, не удалось сформировать корректный ответ. "
            "Попробуйте переформулировать вопрос."
        )

    # Цитаты законов: аккуратно приводим к нашей Pydantic-модели
    raw_citations = core_result.get("citations") or []
    citations: List[Citation] = []
    if isinstance(raw_citations, list):
        for item in raw_citations:
            if not isinstance(item, dict):
                continue
            cid = str(item.get("id") or "").strip()
            if not cid:
                continue
            citations.append(
                Citation(
                    id=cid,
                    title=item.get("title"),
                    url=item.get("url"),
                )
            )

    # Пока ядро не формирует черновик документа — оставляем None.
    # Позже сюда можно будет подкладывать сгенерированный договор/претензию и т.п.
    return AiResponse(
        answer=answer_text,
        citations=citations,
        document_draft=None,
    )

