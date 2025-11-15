from fastapi import APIRouter

router = APIRouter()

# Минимальный рабочий AI-консультант

@router.get("/ping")
async def ping():
    return {"status": "AI module OK"}

@router.post("/ask")
async def ask(question: str):
    # Заглушка, пока не подключим ConsultantCore
    return {
        "answer": f"AI is not configured yet, but received your question: {question}"
    }
