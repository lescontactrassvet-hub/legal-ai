from fastapi import UploadFile
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime


# LEGALAI: АКТИВНЫЕ СХЕМЫ ДЛЯ ШАБЛОНОВ, ДОКУМЕНТОВ, ДЕЛ И ВЛОЖЕНИЙ.


class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None


class TemplateCreate(TemplateBase):
    file: UploadFile


class Template(BaseModel):
    id: int
    file_path: str
    owner_id: int

    class Config:
        orm_mode = True


class TemplateOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    file_path: str
    owner_id: int

    class Config:
        orm_mode = True


class DocumentCreate(BaseModel):
    template_id: int
    values: Dict[str, str]
    generate_pdf: bool = False


class Document(BaseModel):
    id: int
    template_id: int
    user_id: int
    file_path: str
    created_at: datetime

    class Config:
        orm_mode = True


class DocumentOut(BaseModel):
    id: int
    name: str
    file_path: str
    created_at: datetime

    class Config:
        orm_mode = True


class DocumentListItem(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True


# -------- CASES (ДЕЛА) --------


class CaseBase(BaseModel):
    title: Optional[str] = None


class CaseCreate(CaseBase):
    # В реальной реализации user_id берём из токена,
    # здесь передаётся явно для простоты.
    user_id: int


class CaseRead(BaseModel):
    id: int
    user_id: int
    title: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# -------- DOCUMENTS (HTML в редакторе Workspace) --------


class WorkspaceDocumentCreate(BaseModel):
    """
    Создание документа из Workspace.
    content_html — текущее содержимое редактора.
    """
    user_id: int
    name: str
    content_html: str
    case_id: Optional[int] = None


class WorkspaceDocumentUpdate(BaseModel):
    """
    Обновление документа из Workspace.
    Все поля опциональны.
    """
    name: Optional[str] = None
    content_html: Optional[str] = None
    status: Optional[str] = None  # "draft" | "active" | "completed"


class WorkspaceDocumentRead(BaseModel):
    id: int
    case_id: Optional[int]
    user_id: int
    name: Optional[str]
    status: str
    content_html: Optional[str]
    file_path: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# -------- ATTACHMENTS (ВЛОЖЕНИЯ) --------


class AttachmentRead(BaseModel):
    id: int
    case_id: int
    original_name: str
    stored_path: str
    uploaded_at: datetime

    class Config:
        orm_mode = True

