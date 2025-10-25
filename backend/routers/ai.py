"""
AI routes for the Legal AI consultant.

This module defines FastAPI endpoints to interact with the AI system,
including asking questions, checking citations, and suggesting actions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.core import ConsultantCore

router = APIRouter(prefix="/ai", tags=["AI"])
consultant = ConsultantCore()

class QueryRequest(BaseModel):
    query: str

@router.post("/ask")
async def ask(req: QueryRequest):
    """Endpoint for asking the AI a question."""
    try:
        result = await consultant.ask(req.query)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/check")
async def check(req: QueryRequest):
    """Endpoint for checking AI response validity or context."""
    return await consultant.check(req.query)

@router.post("/suggest")
async def suggest(req: QueryRequest):
    """Endpoint for suggesting follow-up actions or additional queries."""
    return await consultant.suggest(req.query)
