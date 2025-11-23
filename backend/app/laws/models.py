from datetime import datetime, date

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Text,
    UniqueConstraint,
)

from app.db import Base


class Law(Base):
    """
    Нормативный акт (закон, указ, постановление и т.п.).
    """

    __tablename__ = "laws"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_laws_source_external_id"),
    )

    id = Column(Integer, primary_key=True, index=True)

    source = Column(String(50), nullable=False, default="pravo.gov.ru")
    external_id = Column(String(255), nullable=False)

    number = Column(String(255), nullable=True)
    title = Column(String(1000), nullable=False)

    summary = Column(Text, nullable=True)

    # ⭐ Новое поле: полный текст нормативного акта из HTML документа
    full_text = Column(Text, nullable=True)

    law_type = Column(String(50), nullable=True)
    country = Column(String(2), nullable=False, default="RU")
    language = Column(String(5), nullable=False, default="ru")

    date_published = Column(Date, nullable=True)
    date_effective = Column(Date, nullable=True)

    link = Column(String(2000), nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
