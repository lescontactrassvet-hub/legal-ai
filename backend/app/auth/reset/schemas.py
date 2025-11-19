from typing import Optional

from pydantic import BaseModel, EmailStr


class ResetStartRequest(BaseModel):
    """Запрос на запуск процедуры восстановления доступа."""
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    birth_year: int
    email: EmailStr
    phone: str
    country: str
    city: str
    comment: Optional[str] = None


class ResetStartResponse(BaseModel):
    status: str
    token_sent: bool = False
    handed_to_operator: bool = False


class ResetVerifyRequest(BaseModel):
    token: str


class ResetVerifyResponse(BaseModel):
    status: str
    valid: bool


class ResetCompleteRequest(BaseModel):
    token: str
    new_username: str
    new_password: str


class ResetCompleteResponse(BaseModel):
    status: str
