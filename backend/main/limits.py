from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from db import get_db
from models.terminal import Terminal
from models.user import User
from models.transaction import Transaction
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter()

class LimitRequest(BaseModel):
    terminal_id: str
    daily_limit: float

@router.post("/set")
def set_limit(req: LimitRequest, db: Session = Depends(get_db)):
    t = db.query(Terminal).filter_by(terminal_id=req.terminal_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Terminal not found")
    t.daily_limit = req.daily_limit
    db.commit()
    return {"msg": "Limit updated"}

@router.get("/usage")
def get_usage(terminal_id: str, db: Session = Depends(get_db)):
    today = datetime.now().date()
    txns = db.query(Transaction).filter(
        Transaction.terminal_id == terminal_id,
        Transaction.status == "Success",
        Transaction.created_at >= today
    ).all()
    total = sum(t.amount for t in txns)
    return {"used_today": total}
