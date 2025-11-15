# SPDX-FileCopyrightText: © Береску Николае
# SPDX-License-Identifier: Proprietary
# Временная заглушка до реализации подтверждения e-mail

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String
from app.database import Base

class EmailToken(Base):
    __tablename__ = "email_tokens"
    __table_args__ = {"extend_existing": True}
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
