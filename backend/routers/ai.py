"""
AI routes for the Legal AI consultant.

This module defines FastAPI endpoints to interact with the AI system, including ask, check, and suggest.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/ask")
async def ask():
    """Endpoint for asking the AI a question."""
    raise NotImplementedError("Ask endpoint not implemented yet")

@router.post("/check")
async def check():
    """Endpoint for checking AI response validity or context."""
    raise NotImplementedError("Check endpoint not implemented yet")

@router.post("/suggest")
async def suggest():
    """Endpoint for suggesting follow-up actions."""
    raise NotImplementedError("Suggest endpoint not implemented yet")
