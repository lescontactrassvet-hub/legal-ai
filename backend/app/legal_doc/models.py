from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base


# LEGALAI: АКТИВНЫЙ РАБОЧИЙ ФАЙЛ МОДЕЛЕЙ ДЛЯ ДОКУМЕНТОВ И ДЕЛ.


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False)
    owner_id = Column(Integer)
    documents = relationship("Document", back_populates="template")


class Case(Base):
    """Дело пользователя: один юридический вопрос + связанные документы и вложения."""

    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    title = Column(
        String,
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    last_user_activity_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    documents = relationship(
        "Document",
        back_populates="case",
        cascade="all, delete-orphan",
    )

    attachments = relationship(
        "Attachment",
        back_populates="case",
        cascade="all, delete-orphan",
    )


class Document(Base):
    """Документ, созданный в рамках дела или на основе шаблона."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    # Шаблон может быть не указан (нестандартный документ)
    template_id = Column(
        Integer,
        ForeignKey("templates.id"),
        nullable=True,
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    # Привязка к делу (для Workspace-логики)
    case_id = Column(
        Integer,
        ForeignKey("cases.id"),
        nullable=True,
        index=True,
    )

    # Имя документа для отображения в списке
    name = Column(
        String,
        nullable=True,
    )

    # Статус жизненного цикла документа
    status = Column(
        String(20),
        nullable=False,
        default="draft",  # для старых записей может быть NULL в БД, в коде мы учитываем это
    )

    # HTML-содержимое из редактора (Workspace)
    content_html = Column(
        Text,
        nullable=True,
    )

    # Путь к финальному файлу (DOCX/PDF) на диске
    file_path = Column(
        String,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Для черновиков: момент авто-удаления (текущее время + 20 дней)
    expires_at = Column(
        DateTime,
        nullable=True,
    )

    template = relationship("Template", back_populates="documents")
    case = relationship("Case", back_populates="documents")

    versions = relationship(
        "DocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentVersion(Base):
    """Версия документа."""

    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )

    content_html = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    document = relationship("Document", back_populates="versions")


class Attachment(Base):
    """Вложенный пользователем файл в рамках дела."""

    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)

    case_id = Column(
        Integer,
        ForeignKey("cases.id"),
        nullable=False,
        index=True,
    )

    original_name = Column(
        String,
        nullable=False,
    )

    stored_path = Column(
        String,
        nullable=False,
    )

    uploaded_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    case = relationship("Case", back_populates="attachments")

