from typing import List, Tuple
import sqlite3
import os


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

        q = f"%{query.strip()}%"

        sql = """
        SELECT
            id,
            content_html
        FROM law_documents
        WHERE content_html IS NOT NULL
          AND content_html LIKE ?
        LIMIT ?
        """

        results: List[Tuple[int, str]] = []

        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(sql, (q, top_k))
            for doc_id, html in cur.fetchall():
                # пока без очистки HTML — отдадим как есть
                results.append((doc_id, html))
        finally:
            conn.close()

        return results
