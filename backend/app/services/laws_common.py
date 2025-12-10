import sqlite3
from datetime import datetime
from typing import Optional


def _get_row_id(row) -> int:
    """
    Вспомогательная функция: достать id и из sqlite3.Row, и из обычного tuple.
    """
    if row is None:
        raise RuntimeError("Row is None, cannot extract id")
    # Если row = sqlite3.Row, можно брать по индексу 0
    return row[0]


def get_or_create_legal_act(
    db: sqlite3.Connection,
    title: str,
    number: Optional[str] = None,
    date: Optional[str] = None,
    jurisdiction: str = "RF",
) -> int:
    """
    Находит или создаёт запись в legal_acts.
    Сейчас упрощённо считаем акт уникальным по title.
    При необходимости позже добавим canonical_key по номеру/дате.
    """
    title = (title or "").strip()
    if not title:
        raise ValueError("Title must not be empty for legal act")

    row = db.execute(
        "SELECT id FROM legal_acts WHERE title = ? LIMIT 1",
        (title,),
    ).fetchone()

    if row:
        return _get_row_id(row)

    now = datetime.utcnow().isoformat()
    canonical_key = title  # временно используем title как canonical_key

    db.execute(
        """
        INSERT INTO legal_acts (
            canonical_key,
            kind,
            number,
            date_adopted,
            jurisdiction,
            title,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            canonical_key,
            None,       # kind
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
    Сохраняет один chunk документа в таблицу documents.
    Пока без дедупликации; при необходимости можно добавить проверку по external_id.
    """
    db.execute(
        """
        INSERT INTO documents (
            act_id,
            source_id,
            external_id,
            chunk_index,
            is_active,
            content
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

