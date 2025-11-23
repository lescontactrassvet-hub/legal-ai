"""
Автоматическая загрузка законов в таблицу laws из официальных источников
(Официальный интернет-портал правовой информации — publication.pravo.gov.ru).

Вариант A:
  - XML RSS-лента (общая):
      https://publication.pravo.gov.ru/rss?rid=1
  - API RSS по блокам:
      http://publication.pravo.gov.ru/api/rss?pageSize=200
      http://publication.pravo.gov.ru/api/rss?block=president&pageSize=200
      http://publication.pravo.gov.ru/api/rss?block=government&pageSize=200
      http://publication.pravo.gov.ru/api/rss?block=council_1&pageSize=200
      http://publication.pravo.gov.ru/api/rss?block=council_2&pageSize=200
      http://publication.pravo.gov.ru/api/rss?block=federal_authorities&pageSize=200
      http://publication.pravo.gov.ru/api/rss?block=court&pageSize=200
      http://publication.pravo.gov.ru/api/rss?block=international&pageSize=200

Все эти URL отдают RSS/XML, поэтому используем единый XML-парсер.

Дубликаты режем по паре (source, external_id).
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import requests
import xml.etree.ElementTree as ET

from app.db import SessionLocal
from app.laws.models import Law

logger = logging.getLogger(__name__)

DEFAULT_SOURCE = "publication.pravo.gov.ru"

# --- Настройки источников -----------------------------------------------------

# Основная XML-лента (можно переопределить через .env при желании)
LAWS_XML_RSS_MAIN = os.getenv("LAWS_XML_RSS_MAIN", "https://publication.pravo.gov.ru/rss?rid=1")

# Базовый URL API /api/rss (можно переопределить, но по умолчанию — официальный)
LAWS_API_BASE = os.getenv("LAWS_API_BASE", "http://publication.pravo.gov.ru/api/rss")

# Дополнительные источники для будущей панели управления
LAWS_EXTRA_SOURCES = [
    url.strip()
    for url in os.getenv("LAWS_EXTRA_SOURCES", "").split(",")
    if url.strip()
]


def _build_api_url(block: Optional[str]) -> str:
    """
    Собирает URL для /api/rss.
    block == None  → общий список,
    block == "president" / "government" / ... → конкретный блок.
    """
    if block:
        return f"{LAWS_API_BASE}?block={block}&pageSize=200"
    return f"{LAWS_API_BASE}?pageSize=200"


# Список официальных API-источников по блокам + их классификация
API_BLOCKS: List[Tuple[Optional[str], str]] = [
    (None, "general"),                        # все публикации
    ("president", "presidential_decree"),    # указы Президента
    ("government", "government_resolution"), # постановления Правительства
    ("council_1", "federal_parliament"),     # Совет Федерации
    ("council_2", "federal_parliament"),     # Госдума
    ("federal_authorities", "ministerial_order"),  # ведомственные акты
    ("court", "court_ruling"),               # судебные решения
    ("international", "international_treaty"),      # международные акты
]


# --- Вспомогательные функции --------------------------------------------------


def _parse_pub_date(value: Optional[str]) -> Optional[datetime]:
    """Пробуем распарсить pubDate из RSS в datetime с UTC-таймзоной."""
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
    """
    Пытаемся вытащить номер документа из заголовка (по шаблону "№ 123-ФЗ" и т.п.).
    Если не получилось — возвращаем None.
    """
    if not title:
        return None
    m = re.search(r"№\s*([^\s,«\"]+)", title)
    if m:
        return f"№ {m.group(1)}"
    return None


def _fetch_xml(url: str) -> ET.Element:
    """Скачивает и парсит XML-документ."""
    logger.info("Загрузка XML RSS: %s", url)
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return ET.fromstring(resp.content)


def fetch_laws_from_rss(url: str) -> List[Dict[str, object]]:
    """
    Универсальный парсер RSS/XML.

    Возвращает список словарей:
      {
        "external_id": str,  # guid или link
        "title": str,
        "link": str,
        "date_published": datetime | None,
        "number": str | None,
      }
    """
    root = _fetch_xml(url)

    items: List[Dict[str, object]] = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or "").strip() or link

        pub_date_raw = item.findtext("pubDate")
        date_published = _parse_pub_date(pub_date_raw)

        number = _extract_number_from_title(title)

        if not link:
            continue

        items.append(
            {
                "external_id": guid,
                "title": title,
                "link": link,
                "date_published": date_published,
                "number": number,
            }
        )

    logger.info("Из RSS %s получено %d элементов", url, len(items))
    return items


def _save_items_to_db(
    items: List[Dict[str, object]],
    law_type: str,
    source: str = DEFAULT_SOURCE,
) -> int:
    """
    Сохраняет элементы в таблицу laws.

    Дубликаты (source, external_id) игнорируются.
    Возвращает количество НОВЫХ записей.
    """
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
            date_published = item.get("date_published")

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
                date_effective=date_published,
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
    """
    Синхронизация по основной XML-ленте (rid=1).
    Считаем её общим потоком "general".

    ВАЖНО: если источник недоступен (timeout, блокировка и т.п.),
    НЕ валим весь процесс синхронизации — просто логируем и продолжаем.
    """
    if not LAWS_XML_RSS_MAIN:
        logger.error("LAWS_XML_RSS_MAIN не задан.")
        return 0

    logger.info("Синхронизация из XML RSS (main): %s", LAWS_XML_RSS_MAIN)

    try:
        items = fetch_laws_from_rss(LAWS_XML_RSS_MAIN)
    except Exception as exc:  # requests.exceptions.RequestException и прочее
        logger.exception(
            "Не удалось загрузить основную XML RSS (%s). "
            "Возможно временные сетевые проблемы или ограничение доступа. "
            "Продолжаем синхронизацию по другим источникам.",
            LAWS_XML_RSS_MAIN,
        )
        return 0

    return _save_items_to_db(items, law_type="general", source=DEFAULT_SOURCE)


def sync_api_blocks() -> int:
    """
    Синхронизация по всем /api/rss?block=...&pageSize=200.

    Для каждого блока используем свой law_type (presidential_decree, government_resolution и т.д.).
    """
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
    """
    Синхронизация с дополнительных источников, заданных в .env (LAWS_EXTRA_SOURCES).

    Это задел для панели управления: позже панель сможет управлять этим списком,
    сейчас он читается из переменной окружения.
    """
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
    """
    Главная точка входа (cron / ручной запуск).

    Вариант A:
      1) Основная XML-лента publication.pravo.gov.ru/rss?rid=1
      2) Все блоки /api/rss?block=...&pageSize=200
      3) Дополнительные источники из LAWS_EXTRA_SOURCES (для панели управления)

    Дубликаты автоматически игнорируются.
    """
    logging.basicConfig(level=logging.INFO)

    logger.info("=== Запуск синхронизации законов (all sources) ===")
    total = 0

    # Даже если XML-лента падает по timeout, мы всё равно идём дальше по API
    total += sync_xml_main()
    total += sync_api_blocks()
    total += sync_extra_sources()

    logger.info("=== Синхронизация завершена. Всего добавлено %d актов. ===", total)
    return total


if __name__ == "__main__":
    # Позволяет запускать: python -m app.laws.sync
    sync_all_sources()
