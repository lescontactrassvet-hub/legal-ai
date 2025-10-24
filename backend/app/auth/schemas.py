from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    """Base fields shared across user schemas."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration input."""
    password: str


class UserLogin(BaseModel):
    """Schema for user login input."""
    username: str | None = None
    email: EmailStr | None = None
    password: str


class UserOut(UserBase):
    """Schema for returning user information."""
    id: int
    is_active: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    """Schema for JWT tokens returned by the login endpoint."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for data extracted from a JWT token payload."""
    username: Optional[str] = None
