from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from models.transaction import Transaction
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
def summary(
    period_days: int = Query(7),
    db: Session = Depends(get_db)
):
    since = datetime.now() - timedelta(days=period_days)
    txns = db.query(Transaction).filter(Transaction.created_at >= since).all()
    total = sum(t.amount for t in txns)
    count = len(txns)
    return {"since": since.strftime("%Y-%m-%d"), "total_amount": total, "count": count}
