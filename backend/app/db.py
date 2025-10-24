from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Import Settings from the parent backend.config to get database URL
from ..config import Settings

# Create a settings instance to access configuration variables
settings = Settings()
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# SQLite specific connection arguments
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our ORM models
Base = declarative_base()

# Dependency for FastAPI routes to get a database session
# This will be used with Depends(get_db)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
