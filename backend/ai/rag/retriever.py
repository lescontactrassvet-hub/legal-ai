from typing import List, Tuple
import sqlite3
import os
import re


DB_PATH = os.getenv(
    "LEGALAI_DB_PATH",
    "/srv/legal-ai/data/legalai.db",
)


class DocumentRetriever:
    """
    SQLite-based RAG retriever for Tatiana.

    Returns list of (document_id, text_fragment)
    from law_documents.content_html.
    """

    def __init__(self):
        self.db_path = DB_PATH

    def retrieve(self, query: str, top_k: int = 8) -> List[Tuple[int, str]]:
        if not query or not query.strip():
            return []
        raw = query.strip().lower()
        parts = re.findall(r"[0-9a-zа-яё]+", raw, flags=re.IGNORECASE)

        tokens: List[str] = []
        seen = set()
        for p in parts:
            if len(p) < 4:
                continue
            if p in seen:
                continue
            seen.add(p)
            tokens.append(p)
            if len(tokens) >= 12:
                break

        if not tokens:
            tokens = [query.strip()]

        like_items = ["content_html LIKE ?"] * len(tokens)
        like_clauses = " OR ".join(like_items)
        sql = """
        SELECT
            id,
            content_html
        FROM law_documents
        WHERE content_html IS NOT NULL
        AND ({like_clauses})
        LIMIT ?
        """
        params = ["%" + t + "%" for t in tokens]
        params.append(top_k)

        results: List[Tuple[int, str]] = []

        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            for doc_id, html in cur.fetchall():
                # пока без очистки HTML — отдадим как есть
                results.append((doc_id, html))
        finally:
            conn.close()

        return results
