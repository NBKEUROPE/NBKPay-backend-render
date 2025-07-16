from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from db import get_db
from models.transaction import Transaction
from models.user import User
from blockchain.erc20 import send_erc20
from blockchain.trc20 import send_trc20
from blockchain.btc import send_btc
from pydantic import BaseModel
from datetime import datetime
import secrets

router = APIRouter()

class CryptoPayoutRequest(BaseModel):
    reference: str
    coin: str  # USDT, USDC, BTC
    network: str  # ERC-20, TRC-20, BTC
    wallet_address: str
    amount: float

class BankPayoutRequest(BaseModel):
    reference: str
    bank_name: str
    account_name: str
    account_number: str
    swift: str
    routing: str = None
    iban: str = None
    amount: float
    currency: str

class PayoutResponse(BaseModel):
    reference: str
    status: str
    payout_txid: str = None
    message: str

@router.post("/crypto", response_model=PayoutResponse)
def crypto_payout(req: CryptoPayoutRequest, db: Session = Depends(get_db)):
    # Find original card transaction
    txn = db.query(Transaction).filter_by(reference=req.reference).first()
    if not txn or txn.status != "Success":
        raise HTTPException(status_code=404, detail="Transaction not found or not eligible")
    if txn.payout_type:
        raise HTTPException(status_code=400, detail="Payout already processed")

    # Blockchain send
    txid = None
    try:
        if req.coin in ("USDT", "USDC") and req.network == "ERC-20":
            txid = send_erc20(req.coin, req.wallet_address, req.amount)
        elif req.coin in ("USDT", "USDC") and req.network == "TRC-20":
            txid = send_trc20(req.coin, req.wallet_address, req.amount)
        elif req.coin == "BTC" and req.network == "BTC":
            txid = send_btc(req.wallet_address, req.amount)
        else:
            raise HTTPException(status_code=400, detail="Unsupported coin/network")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payout error: {str(e)}")

    txn.payout_type = "crypto"
    txn.payout_details = f"{req.coin} {req.network} {req.wallet_address} txid:{txid}"
    txn.status = "Paid"
    txn.updated_at = datetime.now()
    db.commit()
    return PayoutResponse(reference=txn.reference, status="Paid", payout_txid=txid, message="Crypto payout completed.")

@router.post("/bank", response_model=PayoutResponse)
def bank_payout(req: BankPayoutRequest, db: Session = Depends(get_db)):
    txn = db.query(Transaction).filter_by(reference=req.reference).first()
    if not txn or txn.status != "Success":
        raise HTTPException(status_code=404, detail="Transaction not found or not eligible")
    if txn.payout_type:
        raise HTTPException(status_code=400, detail="Payout already processed")
    # Simulate bank payout (replace with real banking API integration)
    txid = f"BANKREF{secrets.randbelow(1_000_000_000)}"
    details = f"{req.bank_name} {req.account_name} {req.account_number} SWIFT:{req.swift} ROUTING:{req.routing or ''} IBAN:{req.iban or ''}"
    txn.payout_type = "bank"
    txn.payout_details = details + f" txid:{txid}"
    txn.status = "Paid"
    txn.updated_at = datetime.now()
    db.commit()
    return PayoutResponse(reference=txn.reference, status="Paid", payout_txid=txid, message="Bank payout completed.")
