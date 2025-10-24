"""
Entry point for the LegalAI backend.

This module re-exports the FastAPI application defined in backend/app/main.py,
allowing you to run the app via `uvicorn backend.main:app`.
"""

from .app.main import app
