from typing import Any, Dict, List, Sequence, Tuple

from .tatyana_profile import TATYANA_SYSTEM_PROMPT
from .rag.retriever import DocumentRetriever
from .rag.ranker import DocumentRanker
from .rag.citation import CitationNormalizer
from .generators.local_gen import LocalGenerator
from .verifiers.safety import SafetyVerifier
from .verifiers.law_guard import LawGuard
from .verifiers.risk_checker import RiskChecker
from .router_rubert import RuBERTIntentClassifier


class ConsultantCore:
    """
    Оркестратор логики юридического консультанта.

    В ЭТОЙ ВЕРСИИ ОН ВСЕГДА РАБОТАЕТ КАК «ТАТЬЯНА»,
    используя системный промпт TATYANA_SYSTEM_PROMPT.
    """

    def __init__(
        self,
        system_prompt: str = TATYANA_SYSTEM_PROMPT,
        retriever: DocumentRetriever | None = None,
        ranker: DocumentRanker | None = None,
        citation_normalizer: CitationNormalizer | None = None,
        generator: LocalGenerator | None = None,
        safety: SafetyVerifier | None = None,
        law_guard: LawGuard | None = None,
        risk_checker: RiskChecker | None = None,
        intent_classifier: RuBERTIntentClassifier | None = None,
    ) -> None:
        self.system_prompt = system_prompt
        self.retriever = retriever or DocumentRetriever()
        self.ranker = ranker or DocumentRanker()
        self.citation_normalizer = citation_normalizer or CitationNormalizer()
        self.generator = generator or LocalGenerator(system_prompt=system_prompt)
        self.safety = safety or SafetyVerifier()
        self.law_guard = law_guard or LawGuard()
        self.risk_checker = risk_checker or RiskChecker()
        self.intent_classifier = intent_classifier or RuBERTIntentClassifier()

    async def ask(self, query: str) -> Dict[str, Any]:
        """
        Основной режим: получить ответ Татьяны с цитатами и анализом рисков.
        """
        clean_query = query.strip()
        if not clean_query:
            raise ValueError(
                "Пустой запрос. Пожалуйста, сформулируйте ваш вопрос или ситуацию."
            )

        # 1. Определяем намерение пользователя
        intent = self.intent_classifier.classify(clean_query)

        # 2. Ищем документы (СИНХРОННЫЙ вызов, без await!)
        docs: Sequence[Tuple[str, str]] = self.retriever.retrieve(
            clean_query, top_k=8
        )

        # 3. Ранжируем документы
        ranked_docs = self.ranker.rank(clean_query, docs)

        # 4. Преобразуем документы в список цитат
        citations = self.citation_normalizer.normalize(ranked_docs)

        # 5. Генерируем ответ
        answer = self.generator.generate(
            query=clean_query,
            context_docs=ranked_docs,
            intent=intent,
        )

        # 6. Проверка безопасности
        if not self.safety.verify(answer):
            raise ValueError(
                "AI-ответ не прошёл проверку безопасности. Попробуйте переформулировать вопрос."
            )

        # 7. Проверка ссылок на нормы (мягкий режим: при ошибке не падаем)
        try:
            validated_citations = self.law_guard.validate_references(citations)
        except Exception:
            validated_citations = citations

        # 8. Анализ рисков
        risk_info = self.risk_checker.analyze(answer)
        # --- ЭТАП 2.8: строгий формат ответа (MODE / DRAFT) ---
        mode = "ANSWER"
        if intent == "template":
            mode = "EDIT"
        elif intent in ("analysis", "risk_check"):
            mode = "ANALYSIS"

        answer_wrapped = wrap_ai_response(
            mode=mode,
            main_text=answer,
            comment="Предложена правка/текст для применения к выбранному фрагменту." if mode == "EDIT" else None,
        )

        return {
            "answer": answer_wrapped,
            "citations": validated_citations,
            "intent": intent,
            "risk_info": risk_info,
        }

    async def check(self, query: str) -> Dict[str, Any]:
        """
        Лёгкий режим: только намерение и список релевантных цитат.
        """
        clean_query = query.strip()
        if not clean_query:
            raise ValueError(
                "Пустой запрос. Пожалуйста, сформулируйте ваш вопрос или ситуацию."
            )

        intent = self.intent_classifier.classify(clean_query)

        docs: Sequence[Tuple[str, str]] = self.retriever.retrieve(
            clean_query, top_k=8
        )
        ranked_docs = self.ranker.rank(clean_query, docs)
        citations = self.citation_normalizer.normalize(ranked_docs)

        try:
            validated_citations = self.law_guard.validate_references(citations)
        except Exception:
            validated_citations = citations

        return {
            "intent": intent,
            "citations": validated_citations,
        }

    async def suggest(self, query: str) -> Dict[str, Any]:
        """
        Подсказки: как лучше сформулировать запрос для Татьяны.
        """
        clean_query = query.strip()
        if not clean_query:
            raise ValueError(
                "Пустой запрос. Опишите, пожалуйста, вашу ситуацию или вопрос."
            )

        intent = self.intent_classifier.classify(clean_query)
        suggestions: List[str] = []

        if intent == "template":
            suggestions.extend(
                [
                    "Уточните, для какого органа и региона нужен документ.",
                    "Добавьте факты: даты, суммы, участников, ключевые события.",
                ]
            )
        elif intent == "risk_check":
            suggestions.extend(
                [
                    "Опишите, какие действия уже были совершены.",
                    "Уточните, каких последствий вы опасаетесь: штраф, расторжение договора, уголовная ответственность и т.п.",
                ]
            )
        elif intent == "analysis":
            suggestions.extend(
                [
                    "Разбейте вашу ситуацию на шаги и задайте несколько конкретных вопросов.",
                    "Укажите, какие документы уже есть (договор, решение суда, уведомления).",
                ]
            )
        else:
            suggestions.append(
                "Сформулируйте вопрос простым языком в одном-двух предложениях: кто, что сделал и чего вы хотите добиться."
            )

        return {
            "intent": intent,
            "suggestions": suggestions,
        }
def wrap_ai_response(mode: str, main_text: str, comment: str | None = None) -> str:
    """
    Этап 2.8 — строгий контракт ответа ИИ (MODE / DRAFT).
    Для EDIT: DRAFT обязателен.
    Для ANSWER/ANALYSIS: обычный текст + END.
    """
    mode = (mode or "").upper().strip()
    if mode not in {"EDIT", "ANALYSIS", "ANSWER"}:
        mode = "ANSWER"

    main_text = (main_text or "").strip()

    if mode == "EDIT":
        if not main_text:
            raise ValueError("EDIT mode requires non-empty DRAFT")

        parts: list[str] = []
        parts.append("<<<MODE:EDIT>>>")
        parts.append("<<<DRAFT>>>")
        parts.append(main_text)
        parts.append("<<<END>>>")
        if comment and comment.strip():
            parts.append("")
            parts.append("<<<COMMENT>>>")
            parts.append(comment.strip())
            parts.append("<<<END>>>")
        return "\n".join(parts)

    # ANALYSIS / ANSWER
    parts: list[str] = []
    parts.append(f"<<<MODE:{mode}>>>")
    parts.append(main_text)
    parts.append("<<<END>>>")
    return "\n".join(parts)

