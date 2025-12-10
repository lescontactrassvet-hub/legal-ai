import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional, Tuple

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

    root = ET.fromstring(resp.text)

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


def process_rss_source(db, source: Dict[str, Any]) -> Tuple[Dict[str, int], Optional[str]]:
    """
    Обрабатывает один источник из law_sources.
    Возвращает (stats, error_message).

    stats = {
        "total":     количество элементов в RSS,
        "processed": сколько попытались обработать,
        "failed":    сколько упало с ошибкой,
        "inserted":  сколько реально вставили в law_documents,
    }
    """
    url = source["base_url"]
    name = source["name"]

    stats = {
        "total": 0,
        "processed": 0,
        "failed": 0,
        "inserted": 0,
    }

    print(f"[pravo_gov_rss] Fetching RSS for source {name} -> {url}")

    try:
        items = fetch_rss(url)
    except Exception as e:
        msg = f"Failed to fetch RSS for {name}: {e}"
        print(f"[pravo_gov_rss] {msg}")
        return stats, msg

    stats["total"] = len(items)
    print(f"[pravo_gov_rss] {name}: received {stats['total']} items")

    for entry in items:
        stats["processed"] += 1

        act_title = entry["title"]
        act_link = entry["link"]

        if not act_link:
            stats["failed"] += 1
            continue

        # 1) создаём / находим акт
        try:
            act_id: Optional[int] = get_or_create_legal_act(
                db=db,
                title=act_title,
                number=None,
                date=None,
                jurisdiction="RF",
            )
        except Exception as e:
            print(
                f"[pravo_gov_rss] Failed to create/find legal act "
                f"'{act_title}': {e}"
            )
            stats["failed"] += 1
            continue

        # 2) скачиваем документ
        try:
            body_resp = requests.get(act_link, timeout=10)
            body_resp.raise_for_status()
            body = body_resp.text
        except Exception as e:
            print(
                f"[pravo_gov_rss] Failed to fetch document {act_link}: {e}"
            )
            stats["failed"] += 1
            continue

        # 3) сохраняем в law_documents
        try:
            save_document_chunk(
                db=db,
                act_id=act_id,
                source_id=source["id"],
                external_id=act_link,
                chunk_index=0,
                text=body,
            )
            stats["inserted"] += 1
        except Exception as e:
            print(
                f"[pravo_gov_rss] Failed to save document chunk for "
                f"{act_link}: {e}"
            )
            stats["failed"] += 1
            continue

    # Если всё прошло без глобальной ошибки — error_message = None
    return stats, None
