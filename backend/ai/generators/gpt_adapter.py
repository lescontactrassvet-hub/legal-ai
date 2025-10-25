"""
Adapter for the GPT external API.

This module defines GPTAdapter which wraps calls to the OpenAI GPT API,
handling authentication, request formation and response parsing.
"""

from typing import Dict, Any
import httpx

class GPTAdapter:
    """
    Adapter to interact with OpenAI's GPT API.
    """

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: str = "https://api.openai.com/v1/chat/completions") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def generate(self, context: str, query: str) -> str:
        """
        Generate a response via the GPT API given context and query.

        Args:
            context: Retrieved context.
            query: User question.

        Returns:
            Generated response string.
        """
        # TODO: implement call to GPT API
        raise NotImplementedError("GPT adapter is not implemented yet.")
