from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, Field, ConfigDict


class LawBase(BaseModel):
    source: str = Field(default="pravo.gov.ru")
    external_id: str
    number: Optional[str] = None
    title: str
    summary: Optional[str] = None
    # полный текст хранится отдельно, может быть очень большим
    full_text: Optional[str] = None
    law_type: Optional[str] = None
    country: str = Field(default="RU")
    language: str = Field(default="ru")
    date_published: Optional[date] = None
    date_effective: Optional[date] = None
    link: Optional[HttpUrl] = None


class LawCreate(LawBase):
    pass


class LawRead(LawBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LawSearchResult(BaseModel):
    id: int
    title: str
    number: Optional[str] = None
    date_effective: Optional[date] = None
    law_type: Optional[str] = None
    link: Optional[HttpUrl] = None

    model_config = ConfigDict(from_attributes=True)
