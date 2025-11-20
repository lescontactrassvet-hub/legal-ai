from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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


@router.post("/ask", response_model=AIAskResponse)
async def ask_ai(request: AIAskRequest) -> AIAskResponse:
    """
    Базовый endpoint для чата с ЮИИ Татьяной.

    Сейчас реализован как "умная заглушка":
    - аккуратно переформулирует вопрос,
    - описывает общий подход,
    - возвращает примерные ссылки на нормы.
    Позже сюда можно будет подключить полноценный AI-модуль.
    """
    query = (request.query or "").strip()
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Слишком короткий запрос.")

    country_h = _human_country(request.country)
    category_h = _human_category(request.category)

    parts: list[str] = []

    parts.append(
        f"Я внимательно прочитала ваше сообщение и постараюсь помочь как ЮИИ Татьяна — ИИ-юрист, "
        f"ориентируясь на законодательство {country_h} и {category_h}, "
        "насколько это позволяет текущая конфигурация системы."
    )

    parts.append(
        "<strong>1. Как я поняла вашу ситуацию</strong><br>"
        f"Сейчас, исходя из вашего описания, ключевой запрос выглядит так: "
        f"<em>«{query}»</em>. "
        "Если я неверно интерпретировала суть вопроса — напишите, пожалуйста, "
        "что именно для вас главное в этой ситуации."
    )

    parts.append(
        "<strong>2. Общий юридический подход</strong><br>"
        "Для подобных ситуаций обычно анализируются: участники отношений, "
        "наличие письменного договора, сроки, суммы, обязательства сторон, "
        "а также документы и переписка. На основании этого подбираются релевантные нормы закона "
        "и судебная практика."
    )

    parts.append(
        "<strong>3. Возможные варианты действий</strong><br>"
        "• Попробовать мирно урегулировать спор (переговоры, досудебная переписка).<br>"
        "• Подготовить претензию или жалобу в компетентный орган.<br>"
        "• Сформировать исковое заявление в суд или заявление в иной орган.<br>"
        "• Параллельно собрать и зафиксировать доказательства (документы, переписку, свидетельские показания)."
    )

    parts.append(
        "<strong>4. Что рекомендую сделать сейчас</strong><br>"
        "1) Кратко по пунктам опишите: когда возникла ситуация, с кем, есть ли письменный договор и какие документы у вас есть.<br>"
        "2) Уточните, чего вы хотите добиться: вернуть деньги, признать договор недействительным, защититься от претензий и т.д.<br>"
        "3) При необходимости загрузите договор или другие материалы через блок анализа файлов — "
        "так я смогу дать более предметный комментарий."
    )

    parts.append(
        "<strong>5. Важное ограничение</strong><br>"
        "Мои ответы носят информационно-справочный характер и не заменяют очную консультацию адвоката или юриста, "
        "особенно в сложных или конфликтных делах."
    )

    answer = "<br><br>".join(parts)

    citations: List[Citation] = []

    if request.country == "RU":
        citations = [
            Citation(
                id="ст. 10 ГК РФ",
                title="Принцип добросовестности в гражданских правоотношениях",
            ),
            Citation(
                id="ст. 12 ГК РФ",
                title="Способы защиты гражданских прав",
            ),
        ]
    elif request.country == "BY":
        citations = [
            Citation(
                id="ст. 8 ГК Республики Беларусь",
                title="Основные начала гражданского законодательства",
            )
        ]
    elif request.country == "UA":
        citations = [
            Citation(
                id="ст. 3 ГК Украины",
                title="Основные принципы гражданского законодательства",
            )
        ]
    elif request.country == "EU":
        citations = [
            Citation(
                id="ст. 6 Конвенции о защите прав человека и основных свобод",
                title="Право на справедливое судебное разбирательство",
            )
        ]
    else:
        citations = [
            Citation(
                id="Общие принципы гражданского законодательства",
                title="Принцип добросовестности и защита нарушенных прав",
            )
        ]

    return AIAskResponse(answer=answer, citations=citations)
