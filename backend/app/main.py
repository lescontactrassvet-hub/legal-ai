from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import Base, engine
from app.legal_doc.routes import router as legal_doc_router
from app.auth.routes import router as auth_router
from app.auth.reset.router import router as reset_router  # модуль восстановления доступа
from routers.ai import router as ai_router  # AI-консультант ЮИИ Татьяна

# --- Sentry (опционально) ---
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastAPIIntegration
except ImportError:
    sentry_sdk = None
# --- конец блока Sentry ---


# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

# Настройки приложения
settings = get_settings()

# Инициализация Sentry ТОЛЬКО если библиотека установлена и DSN задан
if sentry_sdk and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastAPIIntegration()],
        traces_sample_rate=0.0,  # только ошибки, без перфоманса
    )

app = FastAPI(title="LegalAI API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/debug-sentry")
async def debug_sentry():
    """
    Тестовый эндпоинт для проверки интеграции Sentry.
    При обращении специально вызывается ошибка.
    """
    1 / 0


# Роутеры
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
# reset_router уже имеет prefix="/auth" внутри себя, поэтому здесь без prefix
app.include_router(reset_router, tags=["Auth Reset"])
app.include_router(legal_doc_router, prefix="/docs", tags=["Docs"])

# ВАЖНО: prefix НЕ указываем, он уже задан внутри routers/ai.py (prefix="/ai")
app.include_router(ai_router, tags=["AI"])
