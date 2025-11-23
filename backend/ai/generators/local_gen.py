from typing import List, Optional, Sequence, Tuple, Union

from .gigachat_adapter import GigaChatAdapter, GigaChatConfigError

# Документ из RAG: (id, текст)
DocTuple = Tuple[Union[int, str], str]


class LocalGenerator:
    """
    Генератор ответа для Татьяны.

    Логика:
      1. Получает вопрос пользователя и список фрагментов законов (documents).
      2. Собирает из них текстовый контекст.
      3. Пытается использовать GigaChat (если ключи заданы в окружении).
      4. При любой ошибке или отсутствии ключей возвращает локальный fallback-ответ.
    """

    def __init__(
        self,
        max_answer_len: int = 800,
        max_context_len: int = 3000,
        use_gigachat: bool = True,
    ) -> None:
        self.max_answer_len = max_answer_len
        self.max_context_len = max_context_len

        self.gigachat: Optional[GigaChatAdapter] = None
        if use_gigachat:
            try:
                self.gigachat = GigaChatAdapter.from_env()
            except GigaChatConfigError:
                # Ключей нет — тихо работаем только в локальном режиме.
                self.gigachat = None

    # Этот метод вызывает ConsultantCore
    def generate(
        self,
        query: str,
        documents: Sequence[DocTuple],
        intent: Optional[str] = None,
    ) -> str:
        """
        Основной метод генерации ответа.

        query     — вопрос пользователя;
        documents — список (doc_id, fragment);
        intent    — намерение (template / analysis / risk / norm и т.п.).
        """

        if not documents:
            return (
                "Сейчас я не вижу в базе подходящих норм, чтобы дать точный ответ. "
                "Попробуйте сформулировать вопрос более конкретно или уточнить ситуацию. "
                "При серьёзных рисках лучше дополнительно обратиться к юристу."
            )

        context = self._build_context(documents)
        fallback_answer = self._build_fallback_answer(query, context, intent)

        # Если GigaChat не настроен — сразу отдаём fallback.
        if not self.gigachat:
            return fallback_answer

        # Пытаемся спросить GigaChat, но не роняем сервис при ошибках.
        try:
            messages = self._build_messages_for_gigachat(
                query=query,
                context=context,
                intent=intent,
            )
            answer = self.gigachat.chat(messages)
            if not answer:
                return fallback_answer
            return answer[: self.max_answer_len]
        except Exception:
            # Любая ошибка GigaChat → тихий откат на локальный ответ.
            return fallback_answer

    # ---------------- Вспомогательные методы ----------------

    def _build_context(self, documents: Sequence[DocTuple]) -> str:
        """
        Собирает текстовый контекст из фрагментов законов.
        Ограничиваем общую длину, чтобы не раздувать запрос к GigaChat.
        """
        parts: List[str] = []
        current_len = 0

        for idx, (doc_id, fragment) in enumerate(documents, start=1):
            block = f"[Норма {idx} — {doc_id}]\n{fragment.strip()}\n"
            block_len = len(block)
            if current_len + block_len > self.max_context_len:
                break
            parts.append(block)
            current_len += block_len

        return "\n".join(parts)

    def _build_fallback_answer(
        self,
        query: str,
        context: str,
        intent: Optional[str] = None,
    ) -> str:
        """
        Простой локальный ответ без внешнего ИИ: короткое пояснение + выдержки.
        """
        if not context:
            return (
                "Я не нашла подходящих фрагментов законов для ответа. "
                "Попробуйте переформулировать запрос или уточнить тему."
            )

        snippet = context[: self.max_answer_len]

        extra = ""
        if intent == "risk":
            extra = (
                "Обратите особое внимание на возможную ответственность и санкции, "
                "которые могут следовать из указанных норм. "
            )
        elif intent == "template":
            extra = (
                "Ниже приведены выдержки, которые можно использовать для подготовки "
                "черновика документа. "
            )

        return (
            "Я нашла несколько фрагментов нормативных актов, которые относятся "
            "к вашему вопросу. Привожу выдержки (кратко):\n\n"
            f"{snippet}\n\n"
            f"{extra}"
            "Рекомендую изучить указанные нормы и при необходимости обратиться к юристу "
            "для детального анализа вашей ситуации."
        )

    def _build_messages_for_gigachat(
        self,
        query: str,
        context: str,
        intent: Optional[str] = None,
    ) -> List[dict]:
        """
        Формирует messages для GigaChat в формате chat-completions.
        """
        intent_hint = ""
        if intent == "risk":
            intent_hint = (
                "Особое внимание уделяй возможным рискам, ответственности и санкциям "
                "для пользователя. "
            )
        elif intent == "template":
            intent_hint = (
                "Если уместно, предложи структуру документа или пример формулировок. "
            )

        system_prompt = (
            "Ты юридический помощник «Татьяна» в сервисе LegalAI. "
            "Отвечай на русском языке простым и понятным текстом. "
            "Опирайся ТОЛЬКО на переданный контекст с выдержками из законов, "
            "постановлений и других нормативных актов. "
            "Если информации в контексте недостаточно, честно напиши об этом и не придумывай "
            "несуществующие статьи или номера документов."
        )

        user_prompt = (
            f"{intent_hint}"
            "Ниже приведены выдержки из нормативных актов:\n\n"
            f"{context}\n\n"
            f"Вопрос пользователя:\n{query}\n\n"
            "Сформулируй аккуратный юридический ответ, коротко перескажи смысл норм, "
            "укажи возможные действия пользователя. "
            "Не цитируй законы полностью, используй свои формулировки."
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

