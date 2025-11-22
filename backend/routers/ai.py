from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# ВАЖНО: корень проекта в CI/на сервере — папка "backend",
# внутри неё пакеты "app", "ai", "routers" и др.
# Поэтому импортируем так, а не "from backend.ai.core ...".
from ai.core import ConsultantCore

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


class QueryRequest(BaseModel):
    """Запрос к ЮИИ Татьяне."""
    query: str = Field(
        ...,
        min_length=3,
        description="Вопрос пользователя или описание ситуации.",
    )


consultant = ConsultantCore()


@router.post("/ask")
async def ask_endpoint(req: QueryRequest):
    """
    Основной эндпоинт диалога с ЮИИ Татьяной.

    Возвращает словарь вида:
    {
        "answer": "...",
        "citations": [...],
        "intent": "...",
        "risk_info": {...}
    }
    (точная структура зависит от ConsultantCore)
    """
    try:
        return await consultant.ask(req.query)
    except ValueError as e:
        # Контролируемые ошибки валидации/проверок
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Защита от падения оркестратора
        raise HTTPException(status_code=500, detail=f"AI error: {e}")


@router.post("/check")
async def check_endpoint(req: QueryRequest):
    """
    Проверка/поиск норм без развёрнутого ответа.
    Возвращает только ссылки/цитаты и мета-информацию.
    """
    return await consultant.check(req.query)


@router.post("/suggest")
async def suggest_endpoint(req: QueryRequest):
    """
    Подсказки по тому, какой следующий шаг или документ подойдёт.
    Пока может возвращать заглушку — зависит от реализации ConsultantCore.
    """
    return await consultant.suggest(req.query)
