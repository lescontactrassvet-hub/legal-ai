import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from app.services.laws_common import (
    get_or_create_legal_act,
    save_document_chunk,
)
from app.db import get_db


def fetch_rss(url: str) -> list[dict]:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    xml_data = resp.text
    root = ET.fromstring(xml_data)

    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        pub_date = item.findtext("pubDate") or ""

        items.append({
            "title": title.strip(),
            "link": link.strip(),
            "pub_date": pub_date.strip(),
        })
    return items


def process_rss_source(db, source):
    url = source["base_url"]
    items = fetch_rss(url)

    for entry in items:
        act_title = entry["title"]
        act_link = entry["link"]

        act_id = get_or_create_legal_act(
            db=db,
            title=act_title,
            number=None,
            date=None,
            jurisdiction="RF",
        )

        try:
            body = requests.get(act_link, timeout=10).text
        except Exception:
            continue

        save_document_chunk(
            db=db,
            act_id=act_id,
            source_id=source["id"],
            external_id=act_link,
            chunk_index=0,
            text=body,
        )

