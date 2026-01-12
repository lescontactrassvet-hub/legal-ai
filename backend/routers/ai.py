from typing import Optional, List, Tuple
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
# Внутри ConsultantCore — LocalGenerator, который сам решает:
# - использовать GigaChat (если заданы ключи)
# - или работать в локальном режиме (fallback)
consultant_core = ConsultantCore()


def _unwrap_answer(answer: str) -> Tuple[str, Optional[str]]:
    """
    Убирает служебные маркеры этапа 2.8 из answer и, если это EDIT-режим,
    возвращает черновик для document_draft.

    Возвращает:
      plain_answer: str  — чистый текст для чата
      draft: Optional[str] — текст черновика (для редактора), если есть
    """
    if not isinstance(answer, str):
        return str(answer), None

    s = answer.strip()
    if not s.startswith("<<<MODE:"):
        return s, None

    lines = s.splitlines()
    mode = "ANSWER"
    main_lines: List[str] = []
    draft_lines: List[str] = []
    comment_lines: List[str] = []

    state = "NONE"  # NONE | MAIN | DRAFT | COMMENT

    for raw in lines:
        line = raw.strip()

        if line.startswith("<<<MODE:") and line.endswith(">>>"):
            # <<<MODE:EDIT>>>
            try:
                mode = line[len("<<<MODE:") : -3].strip().upper()
            except Exception:
                mode = "ANSWER"
            state = "MAIN"
            continue

        if line == "<<<DRAFT>>>":
            state = "DRAFT"
            continue

        if line == "<<<COMMENT>>>":
            state = "COMMENT"
            continue

        if line == "<<<END>>>":
            state = "NONE"
            continue

        if state == "MAIN":
            main_lines.append(raw)
        elif state == "DRAFT":
            draft_lines.append(raw)
        elif state == "COMMENT":
            comment_lines.append(raw)

    draft = "\n".join(draft_lines).strip() or None
    main_text = "\n".join(main_lines).strip()
    comment = "\n".join(comment_lines).strip() or None

    # Если EDIT и есть draft — в чат отдаём draft, в редактор — draft
    if mode == "EDIT" and draft:
        plain = draft
    else:
        plain = main_text or s

    # COMMENT добавляем как обычный текст, без маркеров
    if comment:
        plain = (plain + "\n\n" + comment).strip()

    return plain, draft


class ChatRequest(BaseModel):
    """
    Запрос к ИИ-консультанту Татьяне.

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

    intent: Optional[str] = Field(
        None, description="Принудительное намерение (если задано фронтом)"
    )

    context: Optional[dict] = Field(
        None, description="Контекст запроса (например, mode=edit_fragment)"
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
        None,
        description="Ссылка на официальный текст (консультант/гарант/госправо)",
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

    Это тонкий слой над ConsultantCore:
    - принимает текст вопроса;
    - проверяет, что текст не пустой и не слишком длинный;
    - определяет intent (RuBERT / fallback);
    - передаёт запрос в ядро;
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

    # Приоритет intent:
    # 1) принудительный от фронта
    # 2) RuBERT
    forced_intent = (payload.intent or "").strip() or None
    core_intent = (
        forced_intent
        or (nlp_info.get("intent") if isinstance(nlp_info, dict) else None)
    )

    core_context = (
        payload.context if isinstance(payload.context, dict) else None
    )

    # === TЗ 5.3: обязательные инструкции по работе с вложениями ===
    ATTACHMENTS_RULES = (
        "ВАЖНО! Если в запросе присутствует блок ТЕКСТ ВЛОЖЕНИЙ, ты ОБЯЗАН:\n"
        "1) Проанализировать каждый файл и его содержимое.\n"
        "2) Использовать информацию из вложений в ответе.\n"
        "3) Явно указывать, из какого файла получена информация.\n"
        "4) Если данных недостаточно или файл непонятен — ЗАДАТЬ УТОЧНЯЮЩИЕ ВОПРОСЫ.\n"
        "5) ЗАПРЕЩЕНО игнорировать вложения или выдумывать факты, которых нет в файлах.\n"
    )
    text = ATTACHMENTS_RULES + "\n" + text

    try:
        # Вызов ядра Татьяны
        core_result = await consultant_core.ask(
            text,
            intent=core_intent,
            context=core_context,
        )
    except ValueError as exc:
        # Ядро может вернуть ValueError для пустых/некорректных запросов
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        # Логируем внутрь, но не раскрываем детали наружу — безопасность
        logger.exception("Ошибка при обработке запроса Татьяной: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=(
                "Сервис ИИ-консультанта Татьяны временно недоступен. "
                "Повторите попытку позже."
            ),
        )

    # Если ядро вернуло не словарь — спасаем ситуацию, приводим к строке
    if not isinstance(core_result, dict):
        answer_text = str(core_result)
        plain_answer, draft = _unwrap_answer(answer_text)
        return AiResponse(
            answer=plain_answer,
            citations=[],
            document_draft=draft,
        )

    # Основной текст ответа
    answer_text = core_result.get("answer")
    if not isinstance(answer_text, str):
        answer_text = (
            "Извините, не удалось сформировать корректный ответ. "
            "Попробуйте переформулировать вопрос."
        )

    # ✅ Убираем мусор и вытаскиваем draft в редактор
    plain_answer, draft = _unwrap_answer(answer_text)
    # Fallback: если модель не вернула <<<DRAFT>>>, но запрос про создание документа — кладём текст в draft
    if draft is None:
        intent_hint = (core_intent or "").lower() if isinstance(core_intent, str) else ""
        text_l = text.lower()
        if intent_hint in {"document_draft", "document_create", "create_document", "template"} or any(
            k in text_l for k in (
                "создай договор",
                "составь договор",
                "подготовь договор",
                "подготовить договор",
                "составить договор",
                "договор аренды",
                "шаблон договора",
            )
        ):
            draft = plain_answer


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

    return AiResponse(
        answer=plain_answer,        # ✅ чистый текст в чат
        citations=citations,
        document_draft=draft,       # ✅ шаблон в редактор
    )

