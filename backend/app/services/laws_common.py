from datetime import datetime
from app.db import get_db


def get_or_create_legal_act(db, title, number=None, date=None, jurisdiction="RF"):
    row = db.execute(
        "SELECT id FROM legal_acts WHERE title = ? LIMIT 1",
        (title,)
    ).fetchone()

    if row:
        return row["id"]

    now = datetime.utcnow().isoformat()

    db.execute("""
        INSERT INTO legal_acts (canonical_key, kind, number, date_adopted,
                               jurisdiction, title, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        None,
        number,
        date,
        jurisdiction,
        title,
        now,
        now
    ))
    db.commit()

    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def save_document_chunk(db, act_id, source_id, external_id, chunk_index, text):
    db.execute("""
       INSERT INTO documents (act_id, source_id, external_id, chunk_index,
                              is_active, content)
       VALUES (?, ?, ?, ?, 1, ?)
    """, (
        act_id, source_id, external_id, chunk_index, text
    ))
    db.commit()

