import sqlite3
from datetime import datetime
from typing import Optional


def _get_row_id(row) -> int:
    """
    Возвращает id из sqlite Row или tuple.
    """
    if row is None:
        raise RuntimeError("Row is None, cannot extract id")
    return row[0]


def get_or_create_legal_act(
    db: sqlite3.Connection,
    title: str,
    number: Optional[str] = None,
    date: Optional[str] = None,
    jurisdiction: str = "RF",
) -> int:
    """
    Создаёт или возвращает ID закона в таблице legal_acts.
    Уникальность — по title (позже сделаем canonical_key).
    """

    title = (title or "").strip()
    if not title:
        raise ValueError("Title must not be empty")

    row = db.execute(
        "SELECT id FROM legal_acts WHERE title = ? LIMIT 1",
        (title,),
    ).fetchone()

    if row:
        return _get_row_id(row)

    now = datetime.utcnow().isoformat()
    canonical_key = title  # временно используем title как ключ

    db.execute(
        """
        INSERT INTO legal_acts (
            canonical_key, kind, number, date_adopted,
            jurisdiction, title, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            canonical_key,
            None,          # kind
            number,
            date,
            jurisdiction,
            title,
            now,
            now,
        ),
    )
    db.commit()

    new_id_row = db.execute("SELECT last_insert_rowid()").fetchone()
    return _get_row_id(new_id_row)


def save_document_chunk(
    db: sqlite3.Connection,
    act_id: Optional[int],
    source_id: int,
    external_id: str,
    chunk_index: int,
    text: str,
) -> int:
    """
    Сохраняет текст документа в documents.content_html.
    Это основной текст закона.
    """

    db.execute(
        """
        INSERT INTO documents (
            act_id,
            source_id,
            external_id,
            chunk_index,
            is_active,
            content_html
        )
        VALUES (?, ?, ?, ?, 1, ?)
        """,
        (
            act_id,
            source_id,
            external_id,
            chunk_index,
            text,
        ),
    )
    db.commit()

    new_id_row = db.execute("SELECT last_insert_rowid()").fetchone()
    return _get_row_id(new_id_row)
