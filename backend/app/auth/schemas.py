from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

    # Дополнительные поля анкеты
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    city: Optional[str] = None
    about: Optional[str] = None

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    last_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    city: Optional[str] = None
    about: Optional[str] = None

    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True

# Новая модель для токена авторизации
class Token(BaseModel):
    access_token: str
    token_type: str
