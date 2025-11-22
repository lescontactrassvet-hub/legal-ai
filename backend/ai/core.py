# backend/ai/core.py

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
        self.generator = generator or LocalGenerator(default_system_prompt=system_prompt)
        self.safety = safety or SafetyVerifier()
        self.law_guard = law_guard or LawGuard()
        self.risk_checker = risk_checker or RiskChecker()
        self.intent_classifier = intent_classifier or RuBERTIntentClassifier()

    async def ask(self, query: str) -> Dict[str, Any]:
        """
        Основной метод: принимает текстовый вопрос пользователя и возвращает
        ответ Татьяны, список цитат и дополнительную информацию о рисках.
        """

        clean_query = (query or "").strip()
        if not clean_query:
            raise ValueError("Пустой запрос. Опишите, пожалуйста, вашу ситуацию или задайте вопрос.")

        # 1. Определяем намерение (тип задачи: шаблон, анализ, проверка, риски и т.п.)
        intent = self.intent_classifier.classify(clean_query)

        # 2. Ищем документы (законы, практику и т.д.) через RAG
        docs: Sequence[Tuple[str, str]] = await self.retriever.retrieve(clean_query, top_k=8)
        ranked_docs: Sequence[Tuple[str, str]] = self.ranker.rank(clean_query, docs)

        # 3. Нормализуем цитаты (подготовка к LawGuard и возвращаемому формату)
        citations = self.citation_normalizer.normalize(ranked_docs)
        citations = self.citation_normalizer.validate_dates(citations)

        # 4. Генерируем ответ, передавая системный промпт Татьяны
        answer: str = self.generator.generate(
            query=clean_query,
            docs=ranked_docs,
            system_prompt=self.system_prompt,
        )

        # 5. Проверка безопасности текста
        if not self.safety.verify(answer):
            raise ValueError(
                "Сформированный ответ не прошёл внутреннюю проверку безопасности. "
                "Повторите запрос, уточните формулировки или обратитесь к живому юристу."
            )

        # 6. Проверка того, что есть хотя бы какие-то ссылки на документы
        # (LawGuard может выбросить исключение, если цитат нет)
        validated_citations = self.law_guard.validate_references(citations)

        # 7. Анализ рисков по тексту
        risk_info = self.risk_checker.analyze(answer)

        return {
            "answer": answer,
            "citations": validated_citations,
            "intent": intent,
            "risk_info": risk_info,
        }

    async def check(self, query: str) -> Dict[str, Any]:
        """
        Упрощённый режим: вернуть только найденные цитаты и тип намерения без подробного ответа.
        """

        clean_query = (query or "").strip()
        if not clean_query:
            raise ValueError("Пустой запрос. Опишите, пожалуйста, вашу ситуацию.")

        intent = self.intent_classifier.classify(clean_query)
        docs = await self.retriever.retrieve(clean_query, top_k=8)
        ranked_docs = self.ranker.rank(clean_query, docs)
        citations = self.citation_normalizer.normalize(ranked_docs)
        citations = self.citation_normalizer.validate_dates(citations)
        validated_citations = self.law_guard.validate_references(citations)

        return {
            "intent": intent,
            "citations": validated_citations,
        }

    async def suggest(self, query: str) -> Dict[str, Any]:
        """
        Режим подсказок: определить, что примерно нужно пользователю
        (тип документа, примерный план действий), без детализированного текста.
        """

        clean_query = (query or "").strip()
        if not clean_query:
            raise ValueError("Пустой запрос. Кратко опишите, что вы хотите сделать.")

        intent = self.intent_classifier.classify(clean_query)

        # Здесь можно расширить логику: на основе intent возвращать подсказки по типу документа, шагам и т.д.
        suggestions: List[str] = []

        if intent == "template":
            suggestions.append(
                "Похоже, вам нужен шаблон документа (договор, претензия, иск и т.п.). "
                "Я могу задать вам вопросы и подготовить черновик."
            )
        elif intent == "risk_check":
            suggestions.append(
                "Запрос касается оценки рисков. Я могу перечислить возможные сценарии, риски и рекомендованные меры."
            )
        elif intent == "analysis":
            suggestions.append(
                "Запрос похож на общую консультацию. Я уточню детали, объясню ваши права и предложу варианты действий."
            )
        else:
            suggestions.append(
                "Я могу помочь вам с анализом ситуации, подготовкой документа или проверкой уже готового текста."
            )

        return {
            "intent": intent,
            "suggestions": suggestions,
        }
