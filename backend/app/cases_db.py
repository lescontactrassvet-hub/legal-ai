import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _sqlite_url(path: str) -> str:
    path = (path or "").strip()
    if not path:
        return ""
    if path.startswith("sqlite:"):
        return path
    if os.path.isabs(path):
        return "sqlite://///" + path.lstrip("/")
    return "sqlite:///" + path

# Prefer systemd env LEGALAI_DB_PATH=/srv/legal-ai/backend/cases.db
_cases_path = os.getenv("LEGALAI_DB_PATH", "").strip()

# Fallback for local/dev: backend/cases.db (one level выше каталога app/)
if not _cases_path:
    _cases_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cases.db"))

CASES_DATABASE_URL = _sqlite_url(_cases_path)

engine = create_engine(
    CASES_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
