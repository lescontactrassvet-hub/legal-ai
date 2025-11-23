"""
Автоматическая загрузка законов в таблицу laws из официального источника
(Официальный интернет-портал правовой информации — publication.pravo.gov.ru).

Логика:
  1) Берём RSS-ленту с портала (URL задаётся через переменную окружения LAWS_RSS_URL_MAIN).
  2) Парсим элементы RSS (title, link, guid, pubDate).
  3) Преобразуем в объекты Law.
  4) Сохраняем в таблицу laws, не создавая дубликаты по (source, external_id).

Вся работа идёт только с уже существующей моделью Law:
  source, external_id, number, title, summary,
  law_type, country, language,
  date_published, date_effective, link, created_at, updated_at
— поля взяты из реального SQL-запроса backend'а.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

import requests
import xml.etree.ElementTree as ET

from app.db import SessionLocal
from app.laws.models import Law

logger = logging.getLogger(__name__)

# Официальный источник
DEFAULT_SOURCE = "publication.pravo.gov.ru"

# URL RSS-ленты берём из .env, чтобы не хардкодить
# (например: https://publication.pravo.gov.ru/rss?rid=1 — "последние опубликованные акты")
LAWS_RSS_URL_MAIN = os.getenv("LAWS_RSS_URL_MAIN")


def _parse_pub_date(value: Optional[str]) -> Optional[datetime]:
    """Пробуем распарсить pubDate из RSS в datetime с UTC-таймзоной."""
    if not value:
        return None
    value = value.strip()
    # Стандартный формат RSS: "Fri, 22 Nov 2025 15:32:00 +0300"
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
    # Очень мягкий шаблон: ищем "№" и всё до конца слова/фразы
    m = re.search(r"№\s*([^\s,«\"]+)", title)
    if m:
        return f"№ {m.group(1)}"
    return None


def fetch_laws_from_rss(url: str) -> List[Dict[str, object]]:
    """
    Загружает и парсит RSS-ленту официального портала.

    Возвращает список словарей:
      {
        "external_id": str,  # guid или link
        "title": str,
        "link": str,
        "date_published": datetime | None,
        "number": str | None,
      }
    """
    logger.info("Загрузка RSS ленты законов: %s", url)
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)

    items: List[Dict[str, object]] = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or "").strip() or link

        pub_date_raw = item.findtext("pubDate")
        date_published = _parse_pub_date(pub_date_raw)

        number = _extract_number_from_title(title)

        if not link:
            # Без ссылки добавлять в базу бессмысленно
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

    logger.info("Из RSS получено %d элементов", len(items))
    return items


def sync_rss_into_db(url: str) -> int:
    """
    Основная функция синхронизации: загружает RSS и записывает новые акты в таблицу laws.

    Возвращает количество НОВЫХ добавленных записей.
    """
    if not url:
        logger.error(
            "LAWS_RSS_URL_MAIN не задан. Укажите URL RSS-канала в переменной окружения."
        )
        return 0

    items = fetch_laws_from_rss(url)
    if not items:
        return 0

    session = SessionLocal()
    created = 0

    try:
        for item in items:
            external_id = str(item["external_id"])
            link = str(item["link"])

            # Проверка на дубликат: та же пара (source, external_id)
            existing = (
                session.query(Law)
                .filter(
                    Law.source == DEFAULT_SOURCE,
                    Law.external_id == external_id,
                )
                .first()
            )
            if existing:
                continue

            title = str(item["title"])
            number = item.get("number")
            date_published = item.get("date_published")

            # Заполняем только то, что знаем точно. Остальное оставляем None.
            law = Law(
                source=DEFAULT_SOURCE,
                external_id=external_id,
                number=number,
                title=title,
                summary=None,
                law_type="federal_act",  # мягкая метка, можно доработать классификацию
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
            logger.info("В таблицу laws добавлено %d новых записей", created)
        else:
            logger.info("Новых законов для добавления нет")

    except Exception:
        session.rollback()
        logger.exception("Ошибка при сохранении законов в базу")
        raise
    finally:
        session.close()

    return created


def sync_all_sources() -> int:
    """
    Точка входа для cron / ручного запуска.

    Сейчас используем только один официальный источник — RSS портала публикаций.
    В будущем сюда можно добавить другие источники (Минюст, Правительство и т.п.).
    """
    if not LAWS_RSS_URL_MAIN:
        logger.error(
            "Переменная LAWS_RSS_URL_MAIN не задана. "
            "Укажите URL RSS-канала publication.pravo.gov.ru в .env."
        )
        return 0

    logger.info("Запуск синхронизации законов из RSS...")
    total = sync_rss_into_db(LAWS_RSS_URL_MAIN)
    logger.info("Синхронизация завершена. Добавлено %d новых актов.", total)
    return total


if __name__ == "__main__":
    # Позволяет запускать: python -m app.laws.sync
    logging.basicConfig(level=logging.INFO)
    sync_all_sources()
