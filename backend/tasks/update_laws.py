import os
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

from app.parsers.pravo_gov_rss import process_rss_source


DEFAULT_DB_PATH = "/srv/legal-ai/data/legalai.db"
BASE_DIR = Path(__file__).resolve().parent.parent
FALLBACK_DB_PATH = BASE_DIR / "data" / "legalai.db"

DB_PATH = os.environ.get("LEGALAI_DB_PATH")
if not DB_PATH:
    if Path(DEFAULT_DB_PATH).exists():
        DB_PATH = DEFAULT_DB_PATH
    else:
        DB_PATH = str(FALLBACK_DB_PATH)


def insert_log_start(db: sqlite3.Connection, source_id: int) -> int:
    """
    Создаёт запись в law_update_log со статусом 'running'.
    Возвращает ID записи.
    """
    started_at = datetime.utcnow().isoformat()
    cur = db.execute(
        """
        INSERT INTO law_update_log (
            source_id,
            started_at,
            status,
            message
        )
        VALUES (?, ?, ?, ?)
        """,
        (source_id, started_at, "running", None),
    )
    db.commit()
    return cur.lastrowid


def update_log_finish(
    db: sqlite3.Connection,
    log_id: int,
    status: str,
    stats: Dict[str, int],
    message: Optional[str] = None,
    details: Optional[str] = None,
) -> None:
    """
    Обновляет запись в law_update_log по завершении обработки источника.
    """
    finished_at = datetime.utcnow().isoformat()

    db.execute(
        """
        UPDATE law_update_log
        SET finished_at    = ?,
            status         = ?,
            message        = ?,
            details        = ?,
            total_items     = ?,
            processed_items = ?,
            failed_items    = ?,
            inserted_items  = ?
        WHERE id = ?
        """,
        (
            finished_at,
            status,
            message,
            details,
            stats.get("total", 0),
            stats.get("processed", 0),
            stats.get("failed", 0),
            stats.get("inserted", 0),
            log_id,
        ),
    )
    db.commit()


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
        source_id = src["id"]
        source_name = src["name"]

        print(f"[update_laws] Processing source: {source_name}")

        log_id = insert_log_start(db, source_id)

        try:
            stats, error_msg = process_rss_source(db, src)

            # Определяем статус
            if error_msg is not None and stats.get("inserted", 0) == 0:
                status = "error"
            elif stats.get("failed", 0) > 0:
                status = "partial"
            else:
                status = "success"

            update_log_finish(
                db,
                log_id=log_id,
                status=status,
                stats=stats,
                message=error_msg or "OK",
                details=None,
            )

        except Exception as e:
            # Любая неожиданная ошибка
            stats = {"total": 0, "processed": 0, "failed": 0, "inserted": 0}
            update_log_finish(
                db,
                log_id=log_id,
                status="error",
                stats=stats,
                message=str(e),
                details=None,
            )

    db.close()
    print("[update_laws] Done.")


if __name__ == "__main__":
    update_all_sources()
