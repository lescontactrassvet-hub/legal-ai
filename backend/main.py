# Re-export FastAPI app from the application package
# This file allows running `uvicorn backend.main:app` to start the application
from .app.main import app  # noqa: F401
"""
Entry point for the LegalAI backend.
This file re-exports the FastAPI app defined in backend/app/main.py so that
running `uvicorn backend.main:app` will launch the application.
"""

from .app.main import app  
