from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict, Optional

# =========================
# Публичный статус использования вложений
# =========================
_LAST_STATUS: Dict[int, Dict[str, str | bool]] = {}

MAX_TEXT_CHARS = 20000


def set_status(att_id: int, used: bool, reason: str, how_to_fix: str = "") -> None:
    _LAST_STATUS[att_id] = {
        "used": used,
        "reason": reason,
        "how_to_fix": how_to_fix,
    }


def get_status(att_id: int) -> Dict[str, str | bool]:
    return _LAST_STATUS.get(att_id, {
        "used": False,
        "reason": "not_processed",
        "how_to_fix": "Файл не обрабатывался.",
    })


# =========================
# Работа с БД cases.db
# =========================
def get_cases_db() -> str:
    return os.getenv(
        "LEGALAI_DB_PATH",
        os.path.join(os.path.dirname(__file__), "..", "cases.db")
    )


def fetch_attachment(att_id: int) -> Optional[dict]:
    db_path = get_cases_db()
    if not os.path.exists(db_path):
        set_status(att_id, False, "cases.db_not_found", "Проверьте путь к cases.db")
        return None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM attachments WHERE id = ?", (att_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    except Exception as e:
        set_status(att_id, False, "db_error", str(e))
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


def resolve_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(backend_root, path)


# =========================
# TXT
# =========================
def extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read().strip()
    return text[:MAX_TEXT_CHARS]


# =========================
# PDF
# =========================
def extract_pdf(path: str) -> str:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise RuntimeError("PyPDF2_not_installed")

    reader = PdfReader(path)
    text = []
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text.append(t)
    return "\n".join(text)[:MAX_TEXT_CHARS]


# =========================
# DOCX
# =========================
def extract_docx(path: str) -> str:
    try:
        from docx import Document
    except ImportError:
        raise RuntimeError("python-docx_not_installed")

    doc = Document(path)
    text = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(text)[:MAX_TEXT_CHARS]


# =========================
# IMG (OCR)
# =========================
def extract_img(path: str) -> str:
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        raise RuntimeError("OCR_dependencies_not_installed")

    img = Image.open(path)
    return pytesseract.image_to_string(img)[:MAX_TEXT_CHARS]


# =========================
# Главная точка входа
# =========================
def extract_attachment_text(att_id: int) -> str:
    att = fetch_attachment(att_id)
    if not att:
        set_status(att_id, False, "attachment_not_found", "Проверьте id вложения")
        return ""

    raw_path = att.get("stored_path")
    if not raw_path:
        set_status(att_id, False, "no_file_path", "В БД отсутствует путь к файлу")
        return ""

    path = resolve_path(raw_path)
    if not os.path.exists(path):
        set_status(att_id, False, "file_not_found", f"Файл не найден: {path}")
        return ""

    ext = os.path.splitext(path)[1].lower()

    try:
        if ext in (".txt", ".md", ".log"):
            text = extract_txt(path)
        elif ext == ".pdf":
            text = extract_pdf(path)
        elif ext == ".docx":
            text = extract_docx(path)
        elif ext in (".png", ".jpg", ".jpeg", ".bmp", ".tiff"):
            text = extract_img(path)
        else:
            set_status(att_id, False, "unsupported_format", f"Формат {ext} не поддержан")
            return ""

        if text.strip():
            set_status(att_id, True, "used")
            return text

        set_status(att_id, False, "empty_text", "Файл не содержит извлекаемого текста")
        return ""

    except RuntimeError as e:
        set_status(att_id, False, str(e), "Установите необходимые зависимости")
        return ""
    except Exception as e:
        set_status(att_id, False, "extract_error", str(e))
        return ""
