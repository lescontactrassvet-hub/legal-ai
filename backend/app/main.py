from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import Base, engine
from .legal_doc.routes import router as legal_doc_router
from .auth.routes import router as auth_router
from .auth.reset.router import router as reset_router  # модуль восстановления доступа
from routers.ai import router as ai_router  # AI-консультант ЮИИ Татьяна

# База законов (локальная БД)
from app.laws.routes import router as laws_router
# Онлайн-обновления законов (парсер, то что было в updates)
from app.updates.routes import router as updates_router
# Загрузка логотипа
from app.admin.logo_upload import router as logo_upload_router

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
if sentry_sdk and getattr(settings, "SENTRY_DSN", None):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastAPIIntegration()],
        traces_sample_rate=0.0,  # только ошибки, без перфоманса
        environment=getattr(settings, "ENVIRONMENT", "production"),
    )

app = FastAPI(
    title="Юридический API",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=getattr(settings, "CORS_ALLOW_ORIGINS", ["*"]),
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


# =========================
#        Роутеры
# =========================

# Авторизация
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(reset_router, tags=["Auth Reset"])

# Документы
app.include_router(legal_doc_router, prefix="/docs", tags=["Docs"])

# AI-консультант (prefix уже внутри routers/ai.py)
app.include_router(ai_router, tags=["AI"])

# База законов (локальная БД /laws/…)
app.include_router(laws_router, tags=["Laws"])

# Онлайн-обновления законов (модуль updates)
app.include_router(updates_router, tags=["Laws Updates"])

# Админка: загрузка логотипа
app.include_router(logo_upload_router, tags=["Admin"])

