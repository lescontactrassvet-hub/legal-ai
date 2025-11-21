from fastapi import APIRouter, UploadFile, File, HTTPException
import os

router = APIRouter(prefix="/admin", tags=["Admin"])

UPLOAD_PATH = "/srv/legal-ai/frontend/dist/Logo.png"

@router.post("/upload-logo")
async def upload_logo(file: UploadFile = File(...)):
    # Проверяем формат
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
        raise HTTPException(status_code=400, detail="Разрешены только файлы PNG или JPG")
    
    # Читаем файл
    content = await file.read()

    # Пишем логотип в нужную папку
    try:
        with open(UPLOAD_PATH, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка записи файла: {e}")

    return {"status": "ok", "message": "Логотип успешно обновлён"}
