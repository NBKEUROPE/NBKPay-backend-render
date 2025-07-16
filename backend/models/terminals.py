from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from db import Base

class Terminal(Base):
    __tablename__ = "terminals"
    id = Column(Integer, primary_key=True, index=True)
    terminal_id = Column(String(32), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    name = Column(String(128), nullable=True)
    location = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
