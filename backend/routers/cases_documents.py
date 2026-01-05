import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# ✅ ИСПРАВЛЕНО: убран prefix="/api", чтобы не было /api/api на проде
router = APIRouter(tags=["Cases & Documents"])


# -----------------------------
# DB helpers
# -----------------------------

def _db_path() -> str:
    # 1) Если задан путь явно — используем его
    env_path = os.getenv("LEGALAI_DB_PATH")
    if env_path:
        return env_path

    # 2) Если задан DATABASE_URL вида sqlite:////abs/path.db или sqlite:///...
    db_url = os.getenv("DATABASE_URL", "")
    if db_url.startswith("sqlite:////"):
        return db_url.replace("sqlite:////", "/")
    if db_url.startswith("sqlite:///"):
        rel = db_url.replace("sqlite:///", "")
        # rel может быть ./data/legalai.db
        return os.path.abspath(rel)

    # 3) Фолбэк для Termux проекта
    return os.path.abspath("data/legalai.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


# -----------------------------
# Schemas (простые модели)
# -----------------------------

class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: Optional[str] = None


class CaseOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: str
    updated_at: str


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    content: Optional[str] = ""  # начальный текст (создаст версию)


class DocumentOut(BaseModel):
    id: int
    case_id: int
    title: str
    type: str
    created_at: str
    updated_at: str


class DocumentVersionCreate(BaseModel):
    content: str = Field(..., min_length=1)
    source: str = Field(..., pattern="^(user|ai)$")  # user / ai


class DocumentVersionOut(BaseModel):
    id: int
    document_id: int
    content: str
    source: str
    created_at: str


# -----------------------------
# CASES
# -----------------------------

@router.get("/cases", response_model=List[CaseOut])
def list_cases() -> List[CaseOut]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, description, created_at, updated_at "
        "FROM cases ORDER BY id DESC"
    )
    rows = cur.fetchall()
    conn.close()
    return [CaseOut(**dict(r)) for r in rows]


@router.post("/cases", response_model=CaseOut)
def create_case(payload: CaseCreate) -> CaseOut:
    conn = _connect()
    cur = conn.cursor()
    now = _now_iso()
    cur.execute(
        "INSERT INTO cases (title, description, created_at, updated_at) "
        "VALUES (?, ?, ?, ?)",
        (payload.title.strip(), payload.description, now, now),
    )
    case_id = cur.lastrowid
    conn.commit()

    cur.execute(
        "SELECT id, title, description, created_at, updated_at FROM cases WHERE id = ?",
        (case_id,),
    )
    row = cur.fetchone()
    conn.close()
    return CaseOut(**dict(row))


@router.get("/cases/{case_id}", response_model=CaseOut)
def get_case(case_id: int) -> CaseOut:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, description, created_at, updated_at FROM cases WHERE id = ?",
        (case_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found")
    return CaseOut(**dict(row))


# -----------------------------
# DOCUMENTS (внутри дела)
# -----------------------------

@router.get("/cases/{case_id}/documents", response_model=List[DocumentOut])
def list_case_documents(case_id: int) -> List[DocumentOut]:
    conn = _connect()
    cur = conn.cursor()

    # Проверим, что дело существует
    cur.execute("SELECT id FROM cases WHERE id = ?", (case_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")

    cur.execute(
        "SELECT id, case_id, title, type, created_at, updated_at "
        "FROM documents WHERE case_id = ? ORDER BY id DESC",
        (case_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [DocumentOut(**dict(r)) for r in rows]


@router.post("/cases/{case_id}/documents", response_model=DocumentOut)
def create_document(case_id: int, payload: DocumentCreate) -> DocumentOut:
    conn = _connect()
    cur = conn.cursor()

    # Проверим, что дело существует
    cur.execute("SELECT id FROM cases WHERE id = ?", (case_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Case not found")

    now = _now_iso()

    cur.execute(
        "INSERT INTO documents (case_id, title, type, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (case_id, payload.title.strip(), payload.type.strip(), now, now),
    )
    document_id = cur.lastrowid

    # Создаём первую версию текста (даже если пусто — оставим пустую строку)
    initial_content = payload.content or ""
    cur.execute(
        "INSERT INTO document_versions (document_id, content, source, created_at) "
        "VALUES (?, ?, ?, ?)",
        (document_id, initial_content, "user", now),
    )

    conn.commit()

    cur.execute(
        "SELECT id, case_id, title, type, created_at, updated_at "
        "FROM documents WHERE id = ?",
        (document_id,),
    )
    row = cur.fetchone()
    conn.close()
    return DocumentOut(**dict(row))


@router.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(document_id: int) -> DocumentOut:
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, case_id, title, type, created_at, updated_at "
        "FROM documents WHERE id = ?",
        (document_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentOut(**dict(row))


# -----------------------------
# VERSIONS (история текста)
# -----------------------------

@router.get("/documents/{document_id}/versions", response_model=List[DocumentVersionOut])
def list_versions(document_id: int) -> List[DocumentVersionOut]:
    conn = _connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM documents WHERE id = ?", (document_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")

    cur.execute(
        "SELECT id, document_id, content, source, created_at "
        "FROM document_versions WHERE document_id = ? ORDER BY id DESC",
        (document_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [DocumentVersionOut(**dict(r)) for r in rows]


@router.post("/documents/{document_id}/versions", response_model=DocumentVersionOut)
def create_version(document_id: int, payload: DocumentVersionCreate) -> DocumentVersionOut:
    conn = _connect()
    cur = conn.cursor()

    cur.execute("SELECT id FROM documents WHERE id = ?", (document_id,))
    if not cur.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")

    now = _now_iso()

    cur.execute(
        "INSERT INTO document_versions (document_id, content, source, created_at) "
        "VALUES (?, ?, ?, ?)",
        (document_id, payload.content, payload.source, now),
    )
    version_id = cur.lastrowid

    # Обновим updated_at у документа (чтобы было видно, что документ менялся)
    cur.execute(
        "UPDATE documents SET updated_at = ? WHERE id = ?",
        (now, document_id),
    )

    conn.commit()

    cur.execute(
        "SELECT id, document_id, content, source, created_at "
        "FROM document_versions WHERE id = ?",
        (version_id,),
    )
    row = cur.fetchone()
    conn.close()
    return DocumentVersionOut(**dict(row))
# -----------------------------
# EXPORT (DOCX / PDF / ZIP)
# из document_versions.content
# -----------------------------
import io
import os
import re
import html as _html
import zipfile
import tempfile
import shutil

from fastapi import Query
from fastapi.responses import StreamingResponse, FileResponse
from starlette.background import BackgroundTask

try:
    from docx import Document as DocxDocument
except Exception:
    DocxDocument = None

try:
    # уже есть в проекте (использует unoconv)
    from app.legal_doc.pdf_utils import convert_docx_to_pdf
except Exception:
    convert_docx_to_pdf = None


def _html_to_text(s: str) -> str:
    if not s:
        return ""
    s = s.replace("\r", "")
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</p\s*>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = _html.unescape(s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s


def _safe_filename(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"[^\w\-. А-Яа-я]+", "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name or "document"


def _get_version_row(cur, document_id: int, version_id: int | None):
    if version_id is not None:
        cur.execute(
            "SELECT id, document_id, content, source, created_at "
            "FROM document_versions WHERE id = ? AND document_id = ?",
            (version_id, document_id),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Version not found")
        return row

    cur.execute(
        "SELECT id, document_id, content, source, created_at "
        "FROM document_versions WHERE document_id = ? ORDER BY id DESC LIMIT 1",
        (document_id,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No versions for this document")
    return row


def _build_docx_bytes(text: str) -> bytes:
    if DocxDocument is None:
        raise HTTPException(status_code=500, detail="python-docx is not installed on server")
    doc = DocxDocument()
    for line in (text or "").split("\n"):
        doc.add_paragraph(line)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()


@router.get("/documents/{document_id}/export.docx")
def export_document_docx(document_id: int, version_id: int | None = Query(default=None)):
    conn = _connect()
    cur = conn.cursor()

    cur.execute("SELECT title FROM documents WHERE id = ?", (document_id,))
    doc_row = cur.fetchone()
    if not doc_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")

    vrow = _get_version_row(cur, document_id, version_id)
    conn.close()

    title = _safe_filename(doc_row["title"])
    v_id = vrow["id"]
    filename = f"{title}_v{v_id}.docx"

    text = _html_to_text(vrow["content"])
    data = _build_docx_bytes(text)

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


@router.get("/documents/{document_id}/export.pdf")
def export_document_pdf(document_id: int, version_id: int | None = Query(default=None)):
    if convert_docx_to_pdf is None:
        raise HTTPException(status_code=500, detail="PDF export backend is not available (convert_docx_to_pdf not found)")

    conn = _connect()
    cur = conn.cursor()

    cur.execute("SELECT title FROM documents WHERE id = ?", (document_id,))
    doc_row = cur.fetchone()
    if not doc_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")

    vrow = _get_version_row(cur, document_id, version_id)
    conn.close()

    title = _safe_filename(doc_row["title"])
    v_id = vrow["id"]
    base = f"{title}_v{v_id}"
    docx_name = f"{base}.docx"
    pdf_name = f"{base}.pdf"

    text = _html_to_text(vrow["content"])
    docx_bytes = _build_docx_bytes(text)

    tmp_dir = tempfile.mkdtemp(prefix="legalai_export_")
    docx_path = os.path.join(tmp_dir, docx_name)
    with open(docx_path, "wb") as f:
        f.write(docx_bytes)

    try:
        pdf_path = convert_docx_to_pdf(docx_path)
    except Exception as exc:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(exc))

    return FileResponse(
        path=pdf_path,
        filename=pdf_name,
        media_type="application/pdf",
        background=BackgroundTask(shutil.rmtree, tmp_dir, ignore_errors=True),
    )


@router.get("/documents/{document_id}/export.zip")
def export_document_zip(document_id: int, version_id: int | None = Query(default=None)):
    conn = _connect()
    cur = conn.cursor()

    cur.execute("SELECT title FROM documents WHERE id = ?", (document_id,))
    doc_row = cur.fetchone()
    if not doc_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")

    vrow = _get_version_row(cur, document_id, version_id)
    conn.close()

    title = _safe_filename(doc_row["title"])
    v_id = vrow["id"]
    base = f"{title}_v{v_id}"
    docx_name = f"{base}.docx"
    pdf_name = f"{base}.pdf"
    zip_name = f"{base}.zip"

    text = _html_to_text(vrow["content"])
    docx_bytes = _build_docx_bytes(text)

    pdf_bytes = None
    tmp_dir = None
    if convert_docx_to_pdf is not None:
        tmp_dir = tempfile.mkdtemp(prefix="legalai_export_")
        docx_path = os.path.join(tmp_dir, docx_name)
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)
        try:
            pdf_path = convert_docx_to_pdf(docx_path)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
        except Exception:
            pdf_bytes = None  # ZIP всё равно отдаём (как минимум DOCX)

    zbio = io.BytesIO()
    with zipfile.ZipFile(zbio, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(docx_name, docx_bytes)
        if pdf_bytes:
            z.writestr(pdf_name, pdf_bytes)
        z.writestr("attachments/README.txt", "Вложения будут добавлены в ZIP после реализации раздела attachments.\n")
    zbio.seek(0)

    headers = {"Content-Disposition": f'attachment; filename="{zip_name}"'}
    resp = StreamingResponse(zbio, media_type="application/zip", headers=headers)
    if tmp_dir:
        resp.background = BackgroundTask(shutil.rmtree, tmp_dir, ignore_errors=True)
    return resp

