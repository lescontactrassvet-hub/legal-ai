# backend/ai/generators/local_gen.py

from typing import List, Optional, Sequence, Tuple

# если у тебя здесь уже есть импорт TATYANA_SYSTEM_PROMPT, можно подтянуть:
# from ..tatyana_profile import TATYANA_SYSTEM_PROMPT

class LocalGenerator:
    """
    Простой генератор ответов.
    Сейчас он НЕ вызывает внешние модели, а формирует развернутый текст на основе найденных фрагментов.
    Позже здесь можно подключить настоящую LLM (локальную или внешнюю), используя system_prompt.
    """

    def __init__(self, default_system_prompt: Optional[str] = None) -> None:
        self.default_system_prompt = default_system_prompt

    def generate(
        self,
        query: str,
        docs: Sequence[Tuple[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Формирует текст ответа.
        - query: вопрос пользователя;
        - docs: список (id, content) найденных документов (законы, решения и т.п.);
        - system_prompt: профиль поведения (например, TATYANA_SYSTEM_PROMPT).
        """

        effective_prompt = system_prompt or self.default_system_prompt

        # Собираем фрагменты документов
        snippets: List[str] = []
        for doc_id, content in docs:
            if not content:
                continue
            # Обрезаем каждый фрагмент, чтобы не раздувать ответ
            snippet = content.strip()
            if len(snippet) > 500:
                snippet = snippet[:500] + "..."
            snippets.append(f"[Документ {doc_id}] {snippet}")

        context_block = "\n\n".join(snippets) if snippets else ""

        # Базовая логика (можно заменить на вызов ЛЛМ позже)
        if not snippets:
            # Нет релевантных документов — даём аккуратный общий комментарий
            base_answer = (
                "Сейчас в моей локальной базе не нашлось явных нормативных актов или судебных "
                "решений, прямо подходящих под вашу ситуацию. Я могу описать общие принципы и "
                "возможные шаги, но настоятельно рекомендую дополнительно проверить актуальные нормы "
                "и, при серьёзных рисках, обратиться к живому юристу."
            )
        else:
            base_answer = (
                "Ниже приведены выдержки из найденных документов, которые могут относиться к вашей ситуации. "
                "Я поясню их смысл простыми словами и предложу возможные шаги.\n\n"
                f"{context_block}"
            )

        # Если есть system_prompt, используем его как «рамку» поведения.
        # Пока мы не подключили настоящую LLM, мы просто добавляем краткое упоминание стиля.
        if effective_prompt:
            return (
                "Я буду отвечать как Татьяна — спокойный и аккуратный юридический консультант, "
                "следуя заданному профилю поведения. Ниже – анализ вашей ситуации.\n\n" + base_answer
            )

        # Фолбэк без промпта
        return base_answer
