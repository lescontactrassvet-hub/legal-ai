from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = "LegalAI"
    secret_key: str = os.getenv("SECRET_KEY", "CHANGE_ME_SUPER_SECRET")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN", "60"))
    algorithm: str = "HS256"
    sqlite_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./legalai.db")

settings = Settings()
