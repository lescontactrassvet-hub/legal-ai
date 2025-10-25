"""
Local language model generator for Consultant.

This module defines LocalGenerator which generates answers from
retrieved context using a locally distilled language model. It is
used when no external service is required.
"""

from typing import List, Dict

class LocalGenerator:
    """
    Generates responses using a local language model.
    """

    def __init__(self) -> None:
        """
        Initialize the local generator (load model, tokenizer, etc.).
        """
        # TODO: load the distilled local model if available
        pass

    async def generate(self, context: str, query: str) -> str:
        """
        Generate a response based on provided context and query.

        Args:
            context: The retrieved textual context.
            query: The user question.

        Returns:
            A generated answer string.
        """
        # TODO: implement local generation
        raise NotImplementedError("Local generation is not implemented yet.")
