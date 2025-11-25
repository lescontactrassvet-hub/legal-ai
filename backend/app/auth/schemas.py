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
    birth_year: Optional[int] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    activity: Optional[str] = None


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True
