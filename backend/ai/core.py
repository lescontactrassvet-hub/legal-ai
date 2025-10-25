"""Core module for the Consultant AI.

This module defines the ConsultantCore orchestrator that coordinates
intent classification, retrieval, generation and verification.
Implementations of these components will be provided in their
respective modules under backend/ai/.
"""

from __future__ import annotations

from typing import Any, Dict


class ConsultantCore:
    """Orchestrator for the legal AI consultant.

    This class is responsible for receiving a user query, routing it to
    the appropriate submodules (e.g., intent classification, RAG
    retriever, generator, verifiers) and returning a structured
    response with citations.

    Note: the current implementation is a placeholder.
    """

    def __init__(self) -> None:
        # initialise sub-components here (e.g. RuBERT router, RAG retriever)
        pass

    async def ask(self, query: str, *, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Process an incoming question and return an AI response.

        Args:
            query: The user question.
            metadata: Optional metadata such as language or user context.

        Returns:
            A dict with the answer and supporting citations.
        """
        raise NotImplementedError("ConsultantCore.ask() is not implemented yet")
