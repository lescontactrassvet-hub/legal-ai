import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional

from app.services.laws_common import (
    get_or_create_legal_act,
    save_document_chunk,
)


def fetch_rss(url: str) -> List[Dict[str, str]]:
    """
    Загружает RSS-ленту и возвращает список элементов:
    {title, link, pub_date}
    """
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    xml_data = resp.text
    root = ET.fromstring(xml_data)

    items: List[Dict[str, str]] = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        pub_date = item.findtext("pubDate") or ""

        items.append(
            {
                "title": title.strip(),
                "link": link.strip(),
                "pub_date": pub_date.strip(),
            }
        )
    return items


def process_rss_source(db, source: Dict[str, Any]) -> None:
    """
    Обрабатывает один источник из law_sources (строка SQLite Row).
    db — это sqlite3.Connection.
    """
    url = source["base_url"]
    name = source["name"]

    print(f"[pravo_gov_rss] Fetching RSS for source {name} -> {url}")

    try:
        items = fetch_rss(url)
    except Exception as e:
        print(f"[pravo_gov_rss] Failed to fetch RSS for {name}: {e}")
        return

    print(f"[pravo_gov_rss] {name}: received {len(items)} items")

    for entry in items:
        act_title = entry["title"]
        act_link = entry["link"]

        if not act_link:
            continue

        # Создаём / находим canonical-акт
        try:
            act_id: Optional[int] = get_or_create_legal_act(
                db=db,
                title=act_title,
                number=None,
                date=None,
                jurisdiction="RF",
            )
        except Exception as e:
            print(f"[pravo_gov_rss] Failed to create/find legal act '{act_title}': {e}")
            act_id = None

        # Получаем текст документа
        try:
            body_resp = requests.get(act_link, timeout=10)
            body_resp.raise_for_status()
            body = body_resp.text
        except Exception as e:
            print(f"[pravo_gov_rss] Failed to fetch document {act_link}: {e}")
            continue

        # Сохраняем один chunk
        try:
            save_document_chunk(
                db=db,
                act_id=act_id,
                source_id=source["id"],
                external_id=act_link,
                chunk_index=0,
                text=body,
            )
        except Exception as e:
            print(f"[pravo_gov_rss] Failed to save document chunk for {act_link}: {e}")
            continue

