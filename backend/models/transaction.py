from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(64), unique=True, index=True, nullable=False)
    terminal_id = Column(String(32), index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    card_masked = Column(String(32), nullable=False)
    protocol = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(8), nullable=False)
    payout_type = Column(String(16), nullable=False)
    payout_details = Column(String(256), nullable=True)
    status = Column(String(16), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
