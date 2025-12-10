import os
import sqlite3
from pathlib import Path

from app.parsers.pravo_gov_rss import process_rss_source


# Путь к БД с законами.
# Можно переопределить через переменную окружения LEGALAI_DB_PATH.
DEFAULT_DB_PATH = "/srv/legal-ai/data/legalai.db"
BASE_DIR = Path(__file__).resolve().parent.parent
FALLBACK_DB_PATH = BASE_DIR / "data" / "legalai.db"

DB_PATH = os.environ.get("LEGALAI_DB_PATH", None)
if not DB_PATH:
    # Если переменная не задана — пробуем серверный путь, иначе backend/data
    if Path(DEFAULT_DB_PATH).exists():
        DB_PATH = DEFAULT_DB_PATH
    else:
        DB_PATH = str(FALLBACK_DB_PATH)


def update_all_sources() -> None:
    print(f"[update_laws] Using DB: {DB_PATH}")
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row

    try:
        sources = db.execute(
            "SELECT * FROM law_sources WHERE is_active = 1"
        ).fetchall()
    except Exception as e:
        db.close()
        raise RuntimeError(f"Failed to read law_sources from DB {DB_PATH}: {e}")

    print(f"[update_laws] Found {len(sources)} active sources")

    for src in sources:
        print(f"[update_laws] Processing source: {src['name']}")
        process_rss_source(db, src)

    db.close()
    print("[update_laws] Done.")


if __name__ == "__main__":
    update_all_sources()

