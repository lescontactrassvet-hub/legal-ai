from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class User(Base):
    """SQLAlchemy model for application users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Profile / registration fields (must be persisted)
    last_name = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    birth_year = Column(Integer, nullable=True)

    phone = Column(String, unique=True, index=True, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)

    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    activity = Column(String, nullable=True)

    company = Column(String, nullable=True)
    position = Column(String, nullable=True)
    about = Column(String, nullable=True)

    # 2FA fields (used by routes_2fa.py)
    totp_secret = Column(String, nullable=True)
    is_2fa_enabled = Column(Boolean, default=False, nullable=False)


    # Relationship to refresh tokens
    tokens = relationship("RefreshToken", back_populates="user")


class RefreshToken(Base):
    """SQLAlchemy model to store refresh tokens for users."""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tokens")
