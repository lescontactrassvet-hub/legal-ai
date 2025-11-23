from typing import List, Tuple

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.laws.models import Law


class DocumentRetriever:
    """
    RAG-ретривер для Татьяны.
    Возвращает список (id, content).
    """

    def __init__(self):
        pass

    def _build_content(self, law: Law) -> str:
        parts = [law.title or ""]
        if law.number:
            parts.append(f"Номер: {law.number}")
        if law.summary:
            parts.append("")
            parts.append(law.summary)
        return "\n".join(parts)

    def retrieve(self, query: str, top_k: int = 8) -> List[Tuple[int, str]]:
        if not query or not query.strip():
            return []

        pattern = f"%{query.strip()}%"

        db: Session = SessionLocal()
        try:
            q = (
                db.query(Law)
                .filter(
                    (Law.title.ilike(pattern)) | (Law.summary.ilike(pattern))
                )
                .order_by(Law.date_effective.desc().nullslast())
                .limit(top_k)
            )
            laws = q.all()
            return [(law.id, self._build_content(law)) for law in laws]
        finally:
            db.close()
