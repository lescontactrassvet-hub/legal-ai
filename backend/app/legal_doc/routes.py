from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import html
import os
import re
from docx import Document

from app.db import get_db
from app.auth.utils import get_current_user
from app.auth.models import User
from .models import Template as TemplateModel, Document as DocumentModel
from .schemas import TemplateOut, DocumentOut, DocumentListItem, DocumentCreate
from .utils import save_template_file, fill_template
from .pdf_utils import convert_docx_to_pdf

router = APIRouter()

def extract_fields_from_docx(path: str) -> List[str]:
    """Extract placeholders enclosed in {{...}} from a DOCX file."""
    placeholders: List[str] = []
    try:
        doc = Document(path)
    except Exception:
        return placeholders
    text = ""
    for paragraph in doc.paragraphs:
        text += " " + paragraph.text
    # Find all occurrences of placeholders {{...}}
    matches = re.findall(r"{{(.*?)}}", text)
    # Remove duplicates while preserving order
    seen = set()
    unique_fields: List[str] = []
    for match in matches:
        field = match.strip()
        if field not in seen:
            seen.add(field)
            unique_fields.append(field)
    return unique_fields

@router.post("/templates", response_model=TemplateOut)
async def upload_template(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Upload a new template. Saves the file to disk and creates a DB entry."""
    # Validate file extension
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only .docx files allowed"
        )
    # Validate file size (<= 5MB)
    try:
        # Determine file size by seeking to end
        current_pos = file.file.tell()
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(current_pos, os.SEEK_SET)
    except Exception:
        size = 0
    if size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large"
        )
    # Validate that it's a proper docx file
    try:
        Document(file.file)
        file.file.seek(0)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid .docx format"
        )
    file_path = save_template_file(file, user.id)
    template = TemplateModel(
        name=name,
        description=description,
        file_path=file_path,
        owner_id=user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.get("/templates", response_model=List[TemplateOut])
async def list_templates(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all templates owned by the current user."""
    templates = db.query(TemplateModel).filter(TemplateModel.owner_id == user.id).all()
    return templates

@router.get("/templates/{id}/fields", response_model=List[str])
async def get_template_fields(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Extract placeholder fields from a template file."""
    template = db.query(TemplateModel).filter(
        TemplateModel.id == id,
        TemplateModel.owner_id == user.id
    ).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    fields = extract_fields_from_docx(template.file_path)
    return fields

@router.post("/documents", response_model=DocumentOut)
async def generate_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Generate a document from a template using provided values."""
    template = db.query(TemplateModel).filter(
        TemplateModel.id == document_data.template_id,
        TemplateModel.owner_id == user.id
    ).first()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    # Ensure provided values correspond to placeholders in the template
    allowed_fields = extract_fields_from_docx(template.file_path)
    for key in document_data.values.keys():
        if key not in allowed_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid field: {key}"
            )
    # Escape HTML to prevent XSS/injection
    cleaned_values = {k: html.escape(v) for k, v in document_data.values.items()}
    file_path = fill_template(template.file_path, cleaned_values)
    # Optionally generate PDF
    if getattr(document_data, "generate_pdf", False):
        try:
            convert_docx_to_pdf(file_path)
        except Exception:
            # If conversion fails, we still proceed with the DOCX
            pass
    name = os.path.basename(file_path)
    document = DocumentModel(
        template_id=template.id,
        user_id=user.id,
        file_path=file_path
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return DocumentOut(
        id=document.id,
        name=name,
        file_path=document.file_path,
        created_at=document.created_at
    )

@router.get("/documents", response_model=List[DocumentListItem])
async def list_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all generated documents for the current user."""
    documents = db.query(DocumentModel).filter(DocumentModel.user_id == user.id).all()
    result: List[DocumentListItem] = []
    for doc in documents:
        result.append(DocumentListItem(
            id=doc.id,
            name=os.path.basename(doc.file_path),
            created_at=doc.created_at
        ))
    return result

@router.get("/documents/{id}")
async def get_document(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Download a generated document by ID."""
    document = db.query(DocumentModel).filter(
        DocumentModel.id == id,
        DocumentModel.user_id == user.id
    ).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    filename = os.path.basename(document.file_path)
    return FileResponse(path=document.file_path, filename=filename, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


# PDF download endpoint
@router.get("/documents/{id}/pdf")
async def get_document_pdf(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Download a generated PDF document by ID. If the PDF doesn't exist, it will be generated from the DOCX."""
    document = db.query(DocumentModel).filter(
        DocumentModel.id == id,
        DocumentModel.user_id == user.id
    ).first()
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    # Determine PDF path
    pdf_path = document.file_path.replace(".docx", ".pdf")
    # Generate PDF if it does not exist
    if not os.path.exists(pdf_path):
        try:
            convert_docx_to_pdf(document.file_path)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    filename = os.path.basename(pdf_path)
    return FileResponse(path=pdf_path, filename=filename, media_type="application/pdf")
