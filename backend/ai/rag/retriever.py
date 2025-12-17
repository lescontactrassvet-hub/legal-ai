from typing import List, Tuple
import sqlite3
import os
import re
try:
    import pymorphy2  # type: ignore
except Exception:
    pymorphy2 = None


# --- C0+: Legal abbreviations normalization ---
LEGAL_ABBR_MAP = {
    "гк": "гражданский кодекс",
    "гкф": "гражданский кодекс",
    "гк рф": "гражданский кодекс",

    "коап": "кодекс об административных правонарушениях",
    "коапф": "кодекс об административных правонарушениях",
    "коап рф": "кодекс об административных правонарушениях",

    "ук": "уголовный кодекс",
    "укрф": "уголовный кодекс",
    "ук рф": "уголовный кодекс",

    "гпк": "гражданский процессуальный кодекс",
    "гпкф": "гражданский процессуальный кодекс",

    "апк": "арбитражный процессуальный кодекс",
    "апкф": "арбитражный процессуальный кодекс",

    "фз": "федеральный закон",
}

MORPH = None
if pymorphy2 is not None:
    try:
        MORPH = pymorphy2.MorphAnalyzer()
    except Exception:
        MORPH = None

def normalize_russian_query(text: str) -> str:
    """
    Lightweight normalization:
    - lowercase
    - normalize 'ё' -> 'е'
    - collapse whitespace
    """
    t = (text or "").strip().lower()
    t = t.replace("ё", "е")
    t = re.sub(r"\s+", " ", t)
    return t


def normalize_legal_abbreviations(text: str) -> str:
    t = text
    for k, v in LEGAL_ABBR_MAP.items():
        t = re.sub(rf"\b{k}\b", v, t)
    return t


# --- C0+: legal references extraction (articles / parts / points) ---
ARTICLE_RE = re.compile(r"(?:ст\.?|статья)\s*(\d+)", re.IGNORECASE)
PART_RE = re.compile(r"(?:ч\.?|часть)\s*(\d+)", re.IGNORECASE)
POINT_RE = re.compile(r"(?:п\.?|пункт)\s*(\d+)", re.IGNORECASE)


def extract_legal_refs(text: str) -> dict:
    return {
        "articles": ARTICLE_RE.findall(text),
        "parts": PART_RE.findall(text),
        "points": POINT_RE.findall(text),
    }


def lemmatize_tokens(tokens: list[str]) -> list[str]:
    if MORPH is None:
        return tokens

    lemmas: list[str] = []
    for t in tokens:
        try:
            p = MORPH.parse(t)[0]
            lemmas.append(p.normal_form)
        except Exception:
            lemmas.append(t)
    return lemmas


DB_PATH = os.getenv(
    "LEGALAI_DB_PATH",
    "/srv/legal-ai/data/legalai.db",
)
USE_FTS = True


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

        raw = normalize_legal_abbreviations(normalize_russian_query(query))
        refs = extract_legal_refs(raw)

        parts = re.findall(r"[0-9a-za-яё]+", raw, flags=re.IGNORECASE)

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

        # must_tokens: extracted article numbers have priority (keep as strings)
        must_tokens = list(dict.fromkeys(refs.get("articles", [])))
        optional_tokens = tokens
        tokens = must_tokens + [t for t in optional_tokens if t not in must_tokens]

        # C0: lemmatize tokens to improve recall across word forms
        tokens = lemmatize_tokens(tokens)

        # B1: FTS5 (bm25) first, fallback to B0 LIKE
        if USE_FTS:
            try:
                fts_terms = [t for t in tokens if t and len(t) >= 2]
                if fts_terms:
                    fts_query = " OR ".join(fts_terms)
                    conn_fts = sqlite3.connect(self.db_path)
                    try:
                        cur_fts = conn_fts.cursor()
                        cur_fts.execute(
                            "SELECT rowid FROM law_documents_fts WHERE law_documents_fts MATCH ? ORDER BY bm25(law_documents_fts) LIMIT ?",
                            (fts_query, top_k),
                        )
                        fts_ids = [r[0] for r in cur_fts.fetchall()]
                        if fts_ids:
                            placeholders = ",".join(["?"] * len(fts_ids))
                            cur_fts.execute(
                                f"SELECT id, content_html FROM law_documents WHERE id IN ({placeholders})",
                                fts_ids,
                            )
                            id_to_html = {row[0]: row[1] for row in cur_fts.fetchall()}
                            fts_results = [(doc_id, id_to_html.get(doc_id) or "") for doc_id in fts_ids if doc_id in id_to_html]
                            if fts_results:
                                return fts_results
                    finally:
                        conn_fts.close()
            except Exception:
                pass


        like_items = ["content_html LIKE ?"] * len(tokens)
        like_clauses = " OR ".join(like_items)

        # IMPORTANT: must be f-string because we inject {like_clauses}
        sql = f"""
        SELECT
        id,
        content_html
        FROM law_documents
        WHERE content_html IS NOT NULL
        AND ({like_clauses})
        LIMIT ?
        """

        params = ["%" + t + "%" for t in tokens]
        candidate_k = max(top_k * 6, 50)
        params.append(candidate_k)

        # keep score internally, then return pairs (doc_id, html)
        results_scored: List[Tuple[int, str, int]] = []

        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.cursor()
            cur.execute(sql, params)
            for doc_id, html in cur.fetchall():
                text = (html or "").lower()
                score = sum(1 for t in tokens if t in text)
                results_scored.append((doc_id, html, score))
        finally:
            conn.close()

        # B0: rank candidates by token match count
        results_scored.sort(key=lambda x: x[2], reverse=True)
        results = [(doc_id, html) for (doc_id, html, _score) in results_scored[:top_k]]
        return results

