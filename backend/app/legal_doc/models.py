from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")
    documents = relationship("Document", back_populates="template")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    template = relationship("Template", back_populates="documents")
    owner = relationship("User")
