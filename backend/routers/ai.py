from typing import List, Optional, Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Абсолютный импорт — ОБЯЗАТЕЛЕН для GitHub Actions
from backend.ai.core import ConsultantCore


router = APIRouter(
    prefix="/ai",
    tags=["ai"],
)


class Citation(BaseModel):
    id: str
    title: Optional[str] = None
    url: Optional[str] = None


class AIAskRequest(BaseModel):
    query: str = Field(..., min_length=3)
    country: Optional[str] = None
    category: Optional[str] = None
    mode: Optional[str] = "dialog"


class AIAskResponse(BaseModel):
    answer: str
    citations: List[Citation] = []


def _human_country(country: Optional[str]) -> str:
    if country == "RU":
        return "Российской Федерации"
    if country == "BY":
        return "Республики Беларусь"
    if country == "UA":
        return "Украины"
    if country == "EU":
        return "Европейского Союза"
    return "выбранной юрисдикции"


def _human_category(category: Optional[str]) -> str:
    mapping = {
        "civil": "гражданское право",
        "criminal": "уголовное право",
        "housing": "жилищные отношения",
        "family": "семейное право",
        "migration": "миграционные вопросы",
    }
    return mapping.get(category or "", "соответствующую отрасль права")


# Создаём Татьяну
consultant = ConsultantCore()


@router.post("/ask", response_model=AIAskResponse)
async def ask_ai(request: AIAskRequest) -> AIAskResponse:
    query = (request.query or "").strip()
    if len(query) < 3:
        raise HTTPException(status_code=400, detail="Слишком короткий запрос.")

    country_h = _human_country(request.country)
    category_h = _human_category(request.category)

    enriched = " ".join([
        f"[Юрисдикция: {request.country} ({country_h})]" if request.country else "",
        f"[Отрасль: {request.category} ({category_h})]" if request.category else "",
        f"[Режим: {request.mode}]" if request.mode else "",
        query
    ])

    try:
        result: Dict[str, Any] = await consultant.ask(enriched)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    raw_answer = result.get("answer", "")
    raw_citations = result.get("citations", [])

    citations = []
    for c in raw_citations:
        if not isinstance(c, dict) and not hasattr(c, "id"):
            continue
        cid = c.get("id") if isinstance(c, dict) else getattr(c, "id")
        title = c.get("title") if isinstance(c, dict) else getattr(c, "title", None)
        url = c.get("url") if isinstance(c, dict) else getattr(c, "url", None)
        if cid:
            citations.append(Citation(id=cid, title=title, url=url))

    if not raw_answer:
        raw_answer = (
            "Не удалось сформировать ответ. Попробуйте уточнить запрос."
        )

    return AIAskResponse(answer=raw_answer, citations=citations)
