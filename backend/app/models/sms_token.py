from sqlalchemy import Column, Integer, String
from app.database import Base

class SmsToken(Base):
    __tablename__ = "sms_tokens"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(32), index=True)
    code = Column(String(10), index=True)
    created_at = Column(Integer, default=0)
