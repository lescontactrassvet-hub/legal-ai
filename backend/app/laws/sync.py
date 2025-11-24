"""
Автоматическая загрузка законов в таблицу laws из официальных источников
(Официальный интернет-портал правовой информации — publication.pravo.gov.ru).
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone, date
from typing import Dict, List, Optional, Tuple

import requests
import xml.etree.ElementTree as ET

from app.db import SessionLocal
from app.laws.models import Law

logger = logging.getLogger(__name__)

DEFAULT_SOURCE = "publication.pravo.gov.ru"

# --- Настройки источников -----------------------------------------------------

LAWS_XML_RSS_MAIN = os.getenv("LAWS_XML_RSS_MAIN", "https://publication.pravo.gov.ru/rss?rid=1")
LAWS_API_BASE = os.getenv("LAWS_API_BASE", "http://publication.pravo.gov.ru/api/rss")

LAWS_EXTRA_SOURCES = [
    url.strip()
    for url in os.getenv("LAWS_EXTRA_SOURCES", "").split(",")
    if url.strip()
]


def _build_api_url(block: Optional[str]) -> str:
    if block:
        return f"{LAWS_API_BASE}?block={block}&pageSize=200"
    return f"{LAWS_API_BASE}?pageSize=200"


API_BLOCKS: List[Tuple[Optional[str], str]] = [
    (None, "general"),
    ("president", "presidential_decree"),
    ("government", "government_resolution"),
    ("council_1", "federal_parliament"),
    ("council_2", "federal_parliament"),
    ("federal_authorities", "ministerial_order"),
    ("court", "court_ruling"),
    ("international", "international_treaty"),
]


# --- Вспомогательные функции --------------------------------------------------


def _parse_pub_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    value = value.strip()
    try:
        dt = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %z")
        return dt.astimezone(timezone.utc)
    except Exception:
        logger.warning("Не удалось распарсить pubDate: %r", value)
        return None


def _extract_number_from_title(title: str) -> Optional[str]:
    if not title:
        return None
    m = re.search(r"№\s*([^\s,«\"]+)", title)
    if m:
        return f"№ {m.group(1)}"
    return None


def _fetch_xml(url: str) -> ET.Element:
    logger.info("Загрузка XML RSS: %s", url)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def fetch_laws_from_rss(url: str) -> List[Dict[str, object]]:
    root = _fetch_xml(url)

    items: List[Dict[str, object]] = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or "").strip() or link

        pub_date_raw = item.findtext("pubDate")
        date_published_dt = _parse_pub_date(pub_date_raw)

        number = _extract_number_from_title(title)

        if not link:
            continue

        items.append(
            {
                "external_id": guid,
                "title": title,
                "link": link,
                "date_published": date_published_dt,
                "number": number,
            }
        )

    logger.info("Из RSS %s получено %d элементов", url, len(items))
    return items


def _to_date(value: Optional[datetime]) -> Optional[date]:
    if isinstance(value, datetime):
        return value.date()
    return None


def _save_items_to_db(
    items: List[Dict[str, object]],
    law_type: str,
    source: str = DEFAULT_SOURCE,
) -> int:
    if not items:
        return 0

    session = SessionLocal()
    created = 0

    try:
        for item in items:
            external_id = str(item["external_id"])
            link = str(item["link"])

            existing = (
                session.query(Law)
                .filter(
                    Law.source == source,
                    Law.external_id == external_id,
                )
                .first()
            )
            if existing:
                continue

            title = str(item["title"])
            number = item.get("number")
            date_published_dt = item.get("date_published")
            date_published = _to_date(date_published_dt)
            date_effective = date_published

            law = Law(
                source=source,
                external_id=external_id,
                number=number,
                title=title,
                summary=None,
                law_type=law_type,
                country="RU",
                language="ru",
                date_published=date_published,
                date_effective=date_effective,
                link=link,
            )

            session.add(law)
            created += 1

        if created:
            session.commit()
            logger.info(
                "В таблицу laws добавлено %d новых записей (law_type=%s, source=%s)",
                created,
                law_type,
                source,
            )
        else:
            logger.info(
                "Новых законов для добавления нет (law_type=%s, source=%s)",
                law_type,
                source,
            )

    except Exception:
        session.rollback()
        logger.exception("Ошибка при сохранении законов в базу")
        raise
    finally:
        session.close()

    return created


# --- Публичные функции синхронизации -----------------------------------------


def sync_xml_main() -> int:
    if not LAWS_XML_RSS_MAIN:
        logger.error("LAWS_XML_RSS_MAIN не задан.")
        return 0

    logger.info("Синхронизация из XML RSS (main): %s", LAWS_XML_RSS_MAIN)

    try:
        items = fetch_laws_from_rss(LAWS_XML_RSS_MAIN)
    except Exception:
        logger.exception(
            "Не удалось загрузить основную XML RSS (%s). "
            "Продолжаем синхронизацию по другим источникам.",
            LAWS_XML_RSS_MAIN,
        )
        return 0

    return _save_items_to_db(items, law_type="general", source=DEFAULT_SOURCE)


def sync_api_blocks() -> int:
    total_created = 0

    for block, law_type in API_BLOCKS:
        url = _build_api_url(block)
        logger.info("Синхронизация из API RSS: %s (law_type=%s)", url, law_type)
        try:
            items = fetch_laws_from_rss(url)
        except Exception:
            logger.exception("Ошибка при загрузке %s", url)
            continue

        created = _save_items_to_db(items, law_type=law_type, source=DEFAULT_SOURCE)
        total_created += created

    return total_created


def sync_extra_sources() -> int:
    total_created = 0
    if not LAWS_EXTRA_SOURCES:
        return 0

    for url in LAWS_EXTRA_SOURCES:
        logger.info("Синхронизация из дополнительного источника: %s", url)
        try:
            items = fetch_laws_from_rss(url)
        except Exception:
            logger.exception("Ошибка при загрузке дополнительного источника %s", url)
            continue

        created = _save_items_to_db(items, law_type="extra", source=url)
        total_created += created

    return total_created


def sync_all_sources() -> int:
    logging.basicConfig(level=logging.INFO)

    logger.info("=== Запуск синхронизации законов (all sources) ===")
    total = 0

    total += sync_xml_main()
    total += sync_api_blocks()
    total += sync_extra_sources()

    logger.info("=== Синхронизация завершена. Всего добавлено %d актов. ===", total)
    return total


if __name__ == "__main__":
    sync_all_sources()
