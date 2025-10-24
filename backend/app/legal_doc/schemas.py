from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class TemplateBase(BaseModel):
    name: str
    description: Optional[str] = None


class TemplateCreate(TemplateBase):
    pass


class Template(TemplateBase):
    id: int
    file_path: str
    owner_id: int

    class Config:
        orm_mode = True


class DocumentCreate(BaseModel):
    template_id: int
    fields: Dict[str, str]


class Document(BaseModel):
    id: int
    template_id: int
    user_id: int
    file_path: str
    created_at: datetime

    class Config:
        orm_mode = True
