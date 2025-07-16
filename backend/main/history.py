from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from models.transaction import Transaction
from models.user import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class TransactionOut(BaseModel):
    reference: str
    date: datetime
    terminal_id: str
    user_id: int
    amount: float
    currency: str
    payout_type: Optional[str]
    payout_details: Optional[str]
    status: str
    card_masked: str
    protocol: str

    class Config:
        orm_mode = True

@router.get("/", response_model=List[TransactionOut])
def get_history(
    db: Session = Depends(get_db),
    terminal_id: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100)
):
    q = db.query(Transaction)
    if terminal_id:
        q = q.filter(Transaction.terminal_id == terminal_id)
    if user_id:
        q = q.filter(Transaction.user_id == user_id)
    if status:
        q = q.filter(Transaction.status == status)
    if start_date:
        q = q.filter(Transaction.created_at >= start_date)
    if end_date:
        q = q.filter(Transaction.created_at <= end_date)
    if search:
        like = f"%{search}%"
        q = q.filter(
            (Transaction.reference.ilike(like)) |
            (Transaction.card_masked.ilike(like)) |
            (Transaction.protocol.ilike(like)) |
            (Transaction.payout_details.ilike(like))
        )
    q = q.order_by(Transaction.created_at.desc()).limit(limit)
    return q.all()
