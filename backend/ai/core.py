from __future__ import annotations
from typing import Any, Dict, List, Optional

from backend.ai.router_rubert import RuBERTIntentClassifier
from backend.ai.rag.retriever import DocumentRetriever
from backend.ai.rag.ranker import DocumentRanker
from backend.ai.rag.citation import CitationNormalizer
from backend.ai.generators.local_gen import LocalGenerator
from backend.ai.verifiers.law_guard import LawGuard
from backend.ai.verifiers.safety import SafetyVerifier


from backend.ai.verifiers.risk_checker import RiskChecker

class ConsultantCore:
    """Orchestrator for the LegalAI consultant.

    Coordinates intent classification, document retrieval, answer generation
    and verification to produce grounded responses with citations.
    """

    def __init__(
        self,
        *,
        intent_classifier: Optional[RuBERTIntentClassifier] = None,
        retriever: Optional[DocumentRetriever] = None,
        ranker: Optional[DocumentRanker] = None,
        citation_normalizer: Optional[CitationNormalizer] = None,
        generator: Optional[LocalGenerator] = None,
        law_guard: Optional[LawGuard] = None,
        safety: Optional[SafetyVerifier] = None,
                    risk_checker: Optional[RiskChecker] = None,

    ) -> None:
        # Initialize sub components; allow dependency injection for testing.
        self.intent_classifier = intent_classifier or RuBERTIntentClassifier()
        self.retriever = retriever or DocumentRetriever()
        self.ranker = ranker or DocumentRanker()
        self.citation_normalizer = citation_normalizer or CitationNormalizer()
        self.generator = generator or LocalGenerator()
        self.law_guard = law_guard or LawGuard()
        self.safety = safety or SafetyVerifier()
                self.risk_checker = risk_checker or RiskChecker()


    async def ask(self, query: str, *, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process an incoming question and return an AI response with citations."""
        if not query:
         

            raise ValueError("Query must not be empty")

        # 1. Intent classification to determine how to handle the query.
        intent = self.intent_classifier.classify(query)

        # 2. Retrieve candidate documents using the RAG retriever.
        docs = await self.retriever.retrieve(query, top_k=8)

        # 3. Rank documents by relevance.
        ranked_docs = self.ranker.rank(query, docs)

        # 4. Normalize citations from the ranked docs.
        citations = self.citation_normalizer.normalize(ranked_docs)

        # 5. Generate a draft answer using the local generator.
          a
                answer = await self.generator.generate(query, ranked_docs, intent=intent)

        # Validate answer safety. Raise error if content is unsafe.
        if not self.safety.verify(answer):
            raise ValueError("Generated content failed safety verification")
        # Validate citations and ensure references are present.
        citations = self.law_guard.validate_references(citations)
        # Analyze risks in the generated answer.
        risk_info = self.risk_checker.analyze(answer)

        return {"answer": answer, "citations": citations, "intent": intent, "risk": risk_info}
ate references and safety.
        # Filter out unsafe or invalid content.
        answer = self.safety.verify(answer)
        citations = self.law_guard.validate_references(citations)

        return {"answer": answer, "citations": citations, "intent": intent}

    async def check(self, text: str, *, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform a legal check of a provided document or statement."""
        # Basic implementation: classify and retrieve normative references.
        intent = self.intent_classifier.classify(text)
        docs = await self.retriever.retrieve(text, top_k=5)
        citations = self.citation_normalizer.normalize(docs)
        return {"intent": intent, "citations": citations}

    async def suggest(self, text: str, *, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Suggest next steps or template use based on the provided input."""
        intent = self.intent_classifier.classify(text)
        # For suggestions we may rely on classification alone.
        # Return suggestions as placeholder.
        suggestions: List[str] = []
        if intent == "template":
            suggestions.append("Consider using a contract template.")
        elif intent == "analysis":
            suggestions.append("Provide more context for a detailed analysis.")
        return {"intent": intent, "suggestions": suggestions}
