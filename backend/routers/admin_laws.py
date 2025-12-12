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
        total = int(cur.fetchone()[0])
        conn.close()
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_law_stats() -> Dict[str, Any]:
    """
    Общая статистика по базе законов:
    - сколько актов (legal_acts)
    - сколько документов (law_documents)
    - идёт ли сейчас обновление (есть ли status='running' без finished_at)
    """
    try:
        conn = _db()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM laws")
        acts_total = int(cur.fetchone()[0])

        cur.execute("SELECT COUNT(*) FROM documents")
        documents_total = int(cur.fetchone()[0])

        cur.execute(
            """
            SELECT COUNT(*)
            FROM law_update_log
            WHERE status = 'running' AND (finished_at IS NULL OR finished_at = '')
            """
        )
        running_count = int(cur.fetchone()[0])

        conn.close()
        return {
            "acts_total": acts_total,
            "documents_total": documents_total,
            "is_running": running_count > 0,
            "running_count": running_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-update")
def run_update() -> Dict[str, Any]:
    """
    Запуск обновления всех активных источников в фоне.
    Возвращает сразу. Защита от двойного запуска через проверку running.
    """
    try:
        import os
        import sys
        import subprocess

        # 1) Проверка: уже идёт обновление?
        conn = _db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COUNT(*)
            FROM law_update_log
            WHERE status = 'running' AND (finished_at IS NULL OR finished_at = '')
            """
        )
        running_count = int(cur.fetchone()[0])
        if running_count > 0:
            conn.close()
            raise HTTPException(status_code=409, detail="Update already running")

        # 2) "Было" — общие числа до запуска
        cur.execute("SELECT COUNT(*) FROM legal_acts")
        before_acts_total = int(cur.fetchone()[0])

        cur.execute("SELECT COUNT(*) FROM law_documents")
        before_documents_total = int(cur.fetchone()[0])

        conn.close()

        # 3) Запуск фонового процесса update_laws (весь апдейт)
        backend_root = Path(__file__).resolve().parents[1]  # .../backend
        env = os.environ.copy()
        env["LEGALAI_DB_PATH"] = str(DB_PATH)

        subprocess.Popen(
            [sys.executable, "-m", "tasks.update_laws"],
            cwd=str(backend_root),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return {
            "ok": True,
            "message": "Update started",
            "before": {
                "acts_total": before_acts_total,
                "documents_total": before_documents_total,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
