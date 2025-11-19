from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db import Base  # используется та же Base, что и в других моделях


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    token = Column(String(128), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class SupportRequest(Base):
    __tablename__ = "support_requests"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(255), index=True, nullable=True)
    phone = Column(String(64), index=True, nullable=True)

    submitted_data = Column(Text, nullable=True)

    status = Column(String(32), default="new", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
