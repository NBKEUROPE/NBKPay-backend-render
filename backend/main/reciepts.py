from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db import get_db
from models.transaction import Transaction
from models.user import User
from pydantic import BaseModel
from typing import Optional
import qrcode
import io
import base64
from fastapi.responses import HTMLResponse

router = APIRouter()

class ReceiptOut(BaseModel):
    reference: str
    date: str
    terminal_id: str
    user_id: int
    amount: float
    currency: str
    payout_type: Optional[str]
    payout_details: Optional[str]
    status: str
    card_masked: str
    protocol: str
    qr_b64: str

    class Config:
        orm_mode = True

def make_qr(data: str) -> str:
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_bytes = buf.getvalue()
    return base64.b64encode(qr_bytes).decode("ascii")

@router.get("/", response_model=ReceiptOut)
def get_receipt(
    reference: str = Query(...),
    db: Session = Depends(get_db)
):
    txn = db.query(Transaction).filter_by(reference=reference).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    qr_b64 = make_qr(reference)
    return ReceiptOut(
        reference=txn.reference,
        date=txn.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        terminal_id=txn.terminal_id,
        user_id=txn.user_id,
        amount=txn.amount,
        currency=txn.currency,
        payout_type=txn.payout_type,
        payout_details=txn.payout_details,
        status=txn.status,
        card_masked=txn.card_masked,
        protocol=txn.protocol,
        qr_b64=qr_b64
    )

@router.get("/html", response_class=HTMLResponse)
def get_receipt_html(
    reference: str = Query(...),
    db: Session = Depends(get_db)
):
    txn = db.query(Transaction).filter_by(reference=reference).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    qr_b64 = make_qr(reference)
    html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Arial,sans-serif; background:#f2f2f2; }}
        .receipt {{ background:#fff; max-width:350px; margin:30px auto; border-radius:16px; box-shadow:0 4px 16px #aaa; padding:24px; }}
        .logo {{ width:50px; }}
        .main {{ font-size:1.1em; color:#d7263d; font-weight:700; }}
        .field {{ margin:8px 0; }}
        .qr {{ margin:14px 0; text-align:center; }}
        .status-ok {{ color:#1a9f45; font-weight:700; }}
        .status-fail {{ color:#d7263d; font-weight:700; }}
    </style>
    </head>
    <body>
      <div class="receipt">
        <div style="display:flex;align-items:center;gap:12px;">
          <img src="https://your-nbkpay-cdn/logo-nbkpay.svg" class="logo" />
          <span class="main">NBK Pay</span>
        </div>
        <div class="field"><b>Date:</b> {txn.created_at.strftime("%Y-%m-%d %H:%M:%S")}</div>
        <div class="field"><b>Terminal:</b> {txn.terminal_id}</div>
        <div class="field"><b>Card:</b> {txn.card_masked}</div>
        <div class="field"><b>Protocol:</b> {txn.protocol}</div>
        <div class="field"><b>Reference:</b> {txn.reference}</div>
        <div class="field"><b>Amount:</b> {txn.amount} {txn.currency}</div>
        <div class="field"><b>Payout:</b> {txn.payout_type or ''} {txn.payout_details or ''}</div>
        <div class="field {'status-ok' if txn.status == 'Paid' else 'status-fail'}"><b>Status:</b> {txn.status}</div>
        <div class="qr">
          <img src="data:image/png;base64,{qr_b64}" width="100"/><br/>
          <span style="font-size:0.95em;color:#2853a8;">Scan for details</span>
        </div>
        <div style="text-align:center;margin-top:18px;color:#999;">Thank you for using NBK Pay</div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

# For email/pdf: Use get_receipt(), render HTML as body or PDF (see notifications.py for sending)
