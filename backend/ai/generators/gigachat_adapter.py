"""
Adapter for the GigaChat external API.

This module defines GigaChatAdapter which wraps calls to the
GigaChat API, handling authentication, request building and
response parsing.
"""

from typing import Dict, Any
import httpx

class GigaChatAdapter:
    """
    Adapter to interact with the GigaChat API.
    """

    def __init__(self, api_key: str, base_url: str = "https://gigachat.example/api") -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def generate(self, context: str, query: str) -> str:
        """
        Generate a response via the GigaChat API using provided context and query.

        Args:
            context: Retrieved context.
            query: User question.

        Returns:
            Generated response from GigaChat.
        """
        # TODO: implement call to GigaChat API
        raise NotImplementedError("GigaChat adapter is not implemented yet.")
