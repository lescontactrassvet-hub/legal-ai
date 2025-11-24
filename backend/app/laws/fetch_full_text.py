"""
Модуль для дозагрузки ПОЛНОГО текста законов в таблицу laws.full_text.

Задача:
  - найти записи, у которых full_text пустой, но есть link;
  - скачать страницу по ссылке;
  - вытащить текст и сохранить в БД.

Запуск НА СЕРВЕРЕ (Ubuntu, прод):
  cd /srv/legal-ai/backend
  .venv/bin/python -m app.laws.fetch_full_text

Запуск локально (Termux, если нужно протестировать):
  cd ~/legal-ai/backend
  .venv/bin/python -m app.laws.fetch_full_text
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.laws.models import Law

# --- Настройка логирования ---

logger = logging.getLogger("laws_full_text")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def _clean_text(text: str) -> str:
    """Минимальная очистка текста: убираем лишние пробелы и пустые строки."""
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip()


def _extract_text_from_html(html: str) -> str:
    """Преобразует HTML документа в простой текст."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n")
    return _clean_text(text)


def fetch_full_text_for_law(law: Law, session: Session, timeout: int = 15) -> Optional[str]:
    """Скачивает и возвращает полный текст для одного закона."""
    if not law.link:
        logger.warning("Law id=%s has no link, skipping", law.id)
        return None

    url = law.link
    logger.info("Fetching full text for law id=%s url=%s", law.id, url)

    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "LegalAI-bot/1.0 (contact: admin@legalai.su)",
            },
        )
    except requests.RequestException as exc:
        logger.error("Request error for law id=%s: %s", law.id, exc)
        return None

    if resp.status_code != 200:
        logger.error(
            "Non-200 status for law id=%s: %s %s",
            law.id,
            resp.status_code,
            resp.reason,
        )
        return None

    try:
        full_text = _extract_text_from_html(resp.text)
    except Exception as exc:
        logger.error("HTML parse error for law id=%s: %s", law.id, exc)
        return None

    if not full_text:
        logger.warning("Empty full_text for law id=%s after parsing", law.id)
        return None

    return full_text


def fetch_full_text_batch(limit: int = 200) -> None:
    """Обрабатывает не более `limit` законов за один запуск.

    Выбирает записи, где full_text пустой, но есть link.
    """
    logger.info("Starting full-text batch for laws (limit=%s)", limit)

    with SessionLocal() as session:
        stmt = (
            select(Law)
            .where(
                (Law.link.isnot(None))
                & ((Law.full_text.is_(None)) | (Law.full_text == ""))
            )
            .order_by(Law.id.asc())
            .limit(limit)
        )

        laws_to_process = session.scalars(stmt).all()

        if not laws_to_process:
            logger.info("No laws found without full_text. Nothing to do.")
            return

        logger.info("Found %s laws to process", len(laws_to_process))

        processed = 0
        updated = 0
        skipped = 0

        for law in laws_to_process:
            processed += 1
            text = fetch_full_text_for_law(law, session=session)

            if not text:
                skipped += 1
                continue

            law.full_text = text
            updated += 1

            try:
                session.add(law)
                session.commit()
            except Exception as exc:
                session.rollback()
                logger.error("DB error while saving law id=%s: %s", law.id, exc)
                skipped += 1

        logger.info(
            "Batch finished: processed=%s, updated=%s, skipped=%s",
            processed,
            updated,
            skipped,
        )


def main() -> None:
    """CLI-точка входа."""
    fetch_full_text_batch(limit=200)


if __name__ == "__main__":
    main()
