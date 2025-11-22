# backend/ai/verifiers/law_guard.py

"""
LawGuard — простой валидатор ссылок на правовые источники.

Сейчас он работает в "мягком" режиме:
- если ссылок нет, он просто возвращает пустой список (НЕ кидает ошибку);
- если ссылки есть, фильтрует странные/битые записи.

Позже сюда можно добавить более строгую проверку
(обязательное наличие закона, валидация формата и т.п.).
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence


class LawGuard:
    """
    Проверка и нормализация списка ссылок (citations),
    которые возвращает RAG/консультант.
    """

    def validate_references(
        self,
        citations: Sequence[Dict[str, Any]] | None,
    ) -> List[Dict[str, Any]]:
        """
        Принимает список словарей вида:
        {"id": "...", "title": "...", "url": "...", ...}

        Возвращает:
        - очищенный список ссылок;
        - если ссылок нет, возвращает пустой список (без ошибок).
        """

        if not citations:
            # ВРЕМЕННО: разрешаем ответы без ссылок, пока база законов не заполнена.
            return []

        normalized: List[Dict[str, Any]] = []

        for item in citations:
            if not isinstance(item, dict):
                # На всякий случай игнорируем странные объекты
                continue

            cid = str(item.get("id") or "").strip()
            if not cid:
                # Ссылка без id нам не подходит
                continue

            title = item.get("title")
            url = item.get("url")

            normalized.append(
                {
                    "id": cid,
                    "title": title,
                    "url": url,
                }
            )

        return normalized
