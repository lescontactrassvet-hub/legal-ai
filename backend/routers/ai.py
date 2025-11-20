from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# ВАЖНО:
# Это первая версия роутера для ЮИИ Татьяны.
# Позже сюда можно будет встроить настоящий AI (LangChain, RAG и т.п.),
# но интерфейс для фронтенда (answer + citations) уже стабильный.

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
        regex="^(RU|BY|UA|EU)$",
    )
    category: Optional[str] = Field(
        None,
        description="Направление права.",
        regex="^(civil|criminal|housing|family|migration)$",
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
    citations: List[Citation] = []


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
    Основной endpoint для чата с ЮИИ Татьяной.

    Сейчас реализован как "умная заглушка":
    - аккуратно переформулирует вопрос,
    - описывает общий подход,
    - возвращает примерные ссылки на нормы,
      чтобы фронтенд мог корректно отобразить блок 'Ссылки на законы'.
    Позже сюда можно будет подключить полноценный AI-модуль.
    """
    query = request.query.strip()

    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Слишком короткий запрос.")

    country_h = _human_country(request.country)
    category_h = _human_category(request.category)

    # Базовый "скелет" ответа в стиле Татьяны.
    # Позже вместо этого блока будет вызов реального AI.
    answer_parts: list[str] = []

    answer_parts.append(
        f"Я внимательно прочитала ваше сообщение и постараюсь помочь как ЮИИ Татьяна — ИИ-юрист, "
        f"ориентируясь на законодательство {country_h} и {category_h}, "
        "насколько это позволяет текущая конфигурация системы."
    )

    answer_parts.append(
        "<strong>1. Как я поняла вашу ситуацию</strong><br>"
        f"Сейчас, исходя из вашего описания, ключевой запрос выглядит так: "
        f"<em>«{query}»</em>. "
        "Если я неверно интерпретировала суть вопроса — напишите, пожалуйста, "
        "что именно для вас главное в этой ситуации."
    )

    answer_parts.append(
        "<strong>2. Общий юридический подход</strong><br>"
        "Как правило, для подобных ситуаций анализ начинается с уточнения фактов: "
        "кто участники отношений, были ли заключены письменные договоры, "
        "какие сроки, суммы, обязательства сторон, есть ли документы или переписка. "
        "На основании этого подбираются релевантные нормы закона и судебная практика."
    )

    answer_parts.append(
        "<strong>3. Варианты действий</strong><br>"
        "Обычно возможны следующие шаги (их набор зависит от деталей дела):<br>"
        "• мирное урегулирование (переговоры, досудебная переписка);<br>"
        "• формирование претензии или жалобы в уполномоченный орган;<br>"
        "• подготовка искового заявления в суд или заявления в иной компетентный орган;<br>"
        "• параллельные меры: сбор доказательств, фиксация переписки, запрос документов.<br>"
        "После уточнения деталей я смогу подсказать, какие варианты в вашем случае более реалистичны."
    )

    answer_parts.append(
        "<strong>4. Что рекомендую сделать сейчас</strong><br>"
        "1) Кратко по пунктам ответьте: когда возникла ситуация, с кем, "
        "есть ли письменный договор и какие именно документы у вас на руках.<br>"
        "2) Уточните, чего вы хотите добиться в итоге: вернуть деньги, признать договор недействительным, "
        "защититься от претензий, изменить условия и т.п.<br>"
        "3) При необходимости загрузите договор или другие документы в раздел анализа файлов — "
        "я смогу более предметно оценить риски и предложить формулировки для документов."
    )

    answer_parts.append(
        "<strong>5. Важное ограничение</strong><br>"
        "Я даю консультации на основе обобщённых правовых подходов и не заменяю очную работу адвоката или юриста, "
        "особенно по сложным делам. Тем не менее, я помогу вам структурировать ситуацию, понять возможные шаги "
        "и подготовить черновики документов."
    )

    answer_text = "<br><br>".join(answer_parts)

    # Временно возвращаем примерные "ссылки на законы".
    # Позже здесь должны быть реальные найденные нормы из вашей базы.
    example_citations: list[Citation] = []

    if request.country == "RU":
        example_citations = [
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
        example_citations = [
            Citation(
                id="ст. 8 ГК Республики Беларусь",
                title="Основные начала гражданского законодательства",
            )
        ]
    elif request.country == "UA":
        example_citations = [
            Citation(
                id="ст. 3 ГК Украины",
                title="Основные принципы гражданского законодательства",
            )
        ]
    elif request.country == "EU":
        example_citations = [
            Citation(
                id="ст. 6 Конвенции о защите прав человека и основных свобод",
                title="Право на справедливое судебное разбирательство",
            )
        ]
    else:
        # Если страна не указана — даём общие ссылки-заглушки.
        example_citations = [
            Citation(
                id="Общие принципы гражданского законодательства",
                title="Принцип добросовестности и защита нарушенных прав",
            )
        ]

    return AIAskResponse(
        answer=answer_text,
        citations=example_citations,
    )
