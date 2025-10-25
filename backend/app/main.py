from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .auth.routes import router as auth_router
from .legal_doc.routes import router as legal_doc_router



Base.metadata.create_all(bind=engine)

# Instantiate FastAPI application
app = FastAPI(title="LegalAI Backend", version="0.1.0")

# Enable CORS middleware (allow all origins for simplicity)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for health check
@app.get("/")
def read_root():
    return {"message": "LegalAI backend is running"}



# Include authentication routes
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(legal_doc_router, prefix="/docs", tags=["Documents"])
