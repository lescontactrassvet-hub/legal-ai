
import base64
import os
import time
import uuid
from typing import Dict, List, Optional, Union

import httpx


class GigaChatConfigError(Exception):
    """Ошибка конфигурации GigaChat (нет client_id / client_secret)."""


class GigaChatAdapter:
    """
    Адаптер для работы с GigaChat через HTTP API.

    Делает:
    - получение и кеширование access_token;
    - вызов /chat/completions;
    - спокойная обработка ошибок (fallback).
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: str = "GIGACHAT_API_PERS",
        auth_url: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        chat_url: str = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        verify: Union[bool, str] = False,
        model: str = "GigaChat",
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.auth_url = auth_url
        self.chat_url = chat_url
        self.verify = verify
        self.model = model

        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0

    # ---------------------------------------------------------------
    #   ИНИЦИАЛИЗАЦИЯ ИЗ ОКРУЖЕНИЯ
    # ---------------------------------------------------------------

    @classmethod
    def from_env(cls) -> "GigaChatAdapter":
        client_id = os.getenv("GIGACHAT_CLIENT_ID")
        client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise GigaChatConfigError(
                "GigaChat не настроен: отсутствуют GIGACHAT_CLIENT_ID / GIGACHAT_CLIENT_SECRET"
            )

        scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

        auth_url = os.getenv(
            "GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        )
        chat_url = os.getenv(
            "GIGACHAT_API_URL",
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        )

        ca_bundle = os.getenv("GIGACHAT_CA_BUNDLE")
        verify: Union[bool, str] = ca_bundle if ca_bundle else False

        return cls(
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            auth_url=auth_url,
            chat_url=chat_url,
            verify=verify,
        )

    # ---------------------------------------------------------------
    #   ПОЛУЧЕНИЕ ТОКЕНА
    # ---------------------------------------------------------------

    def _get_access_token(self) -> str:
        now = time.time()
        if self._access_token and now < self._expires_at - 30:
            return self._access_token

        auth_key = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode("utf-8")
        ).decode("utf-8")

        headers = {
            "Authorization": f"Basic {auth_key}",
            "Content-Type": "application/x-www-form-urlencoded",
            "RqUID": str(uuid.uuid4()),
        }

        data = {"scope": self.scope}

        response = httpx.post(
            self.auth_url,
            headers=headers,
            data=data,
            verify=self.verify,
            timeout=20.0,
        )
        response.raise_for_status()

        payload = response.json()
        access_token = payload.get("access_token")
        if not access_token:
            raise RuntimeError("GigaChat: не удалось получить access_token")

        expires_in = float(payload.get("expires_in", 1800))
        self._access_token = access_token
        self._expires_at = now + expires_in

        return access_token

    # ---------------------------------------------------------------
    #   ВЫЗОВ CHAT / COMPLETIONS
    # ---------------------------------------------------------------

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:
        token = self._get_access_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = httpx.post(
            self.chat_url,
            headers=headers,
            json=payload,
            verify=self.verify,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()

        try:
            return (
                data["choices"][0]["message"]["content"]
                .strip()
            )
        except Exception as exc:
            raise RuntimeError(f"GigaChat: неожиданный формат ответа: {exc}") from exc

