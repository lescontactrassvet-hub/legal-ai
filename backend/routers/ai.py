from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, HttpUrl

router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)

MAX_QUESTION_LEN = 4000


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
        description="Краткое обозначение нормы: ст. 10 ГК РФ, Постановление Правительства № ... и т.п.",
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

    На этом этапе работает в демонстрационном режиме:
    - принимает текст вопроса;
    - возвращает понятный пользователю ответ;
    - формирует примерный черновик документа;
    - структуру ответа мы делаем сразу "боевую", чтобы позже просто
      подключить реальный ИИ/БД законов без изменений фронтенда.
    """
    text = payload.normalized_text()
    if not text:
        raise HTTPException(status_code=400, detail="Пустой запрос")

    # На всякий случай ограничим длину, чтобы не убить бэкенд слишком длинным текстом
    if len(text) > MAX_QUESTION_LEN:
        text = text[:MAX_QUESTION_LEN]

    # TODO: сюда позже подключим реальный анализ законодательства и моделей ИИ
    base_answer = (
        "Пока ИИ-консультант Татьяна работает в демонстрационном режиме.\n\n"
        "Ваш запрос:\n"
        f"«{text}»\n\n"
        "На следующем этапе мы подключим полноценный анализ законодательства, "
        "поиск по базе законов и генерацию формулировок. "
        "Пожалуйста, используйте этот ответ только как черновик и обязательно "
        "проверьте его перед применением."
    )

    draft = (
        "ЧЕРНОВИК ДОКУМЕНТА (демо-режим)\n\n"
        f"Основание: запрос пользователя «{text}».\n\n"
        "Здесь будет формироваться текст договора, заявления или иного документа. "
        "После подключения базы законов и моделей Татьяна сможет подставлять "
        "конкретные статьи и более точные формулировки.\n"
    )

    return AiResponse(
        answer=base_answer,
        citations=[],  # позже сюда добавим реальные ссылки на нормы
        document_draft=draft,
    )
