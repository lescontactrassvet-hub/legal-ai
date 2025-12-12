from pathlib import Path
from typing import Any, Dict, List

import sqlite3
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/admin/laws")


def _detect_db_path() -> Path:
    server_path = Path("/srv/legal-ai/data/legalai.db")
    if server_path.exists():
        return server_path

    local_path = Path(__file__).resolve().parents[1] / "data" / "legalai.db"
    if local_path.exists():
        return local_path

    raise FileNotFoundError(f"legalai.db not found: {server_path} or {local_path}")


DB_PATH = _detect_db_path()


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/sources")
def list_sources() -> List[Dict[str, Any]]:
    try:
        conn = _db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                s.id, s.name, s.type, s.parser, s.base_url, s.is_active,
                l.status AS last_status,
                l.message AS last_message,
                l.total_items AS last_total_items,
                l.processed_items AS last_processed_items,
                l.inserted_items AS last_inserted_items,
                l.failed_items AS last_failed_items,
                l.started_at AS last_started_at,
                l.finished_at AS last_finished_at
            FROM law_sources s
            LEFT JOIN law_update_log l
              ON l.id = (
                 SELECT id FROM law_update_log
                 WHERE source_id = s.id
                 ORDER BY id DESC LIMIT 1
              )
            ORDER BY s.id ASC
            """
        )
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/update-log")
def list_update_log(limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    try:
        conn = _db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                id, source_id, status, message, details,
                total_items, processed_items, failed_items, inserted_items,
                started_at, finished_at
            FROM law_update_log
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        items = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT COUNT(*) FROM law_update_log")
        total = cur.fetchone()[0]
        conn.close()
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

