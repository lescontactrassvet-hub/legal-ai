from app.db import get_db
from app.parsers.pravo_gov_rss import process_rss_source


def update_all_sources():
    db = get_db()
    sources = db.execute(
        "SELECT * FROM law_sources WHERE is_active = 1"
    ).fetchall()

    for src in sources:
        process_rss_source(db, src)


if __name__ == "__main__":
    update_all_sources()

