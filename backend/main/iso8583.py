from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from db import get_db
from models.transaction import Transaction
from models.user import User
from pydantic import BaseModel
import secrets
from datetime import datetime

router = APIRouter()

# Example: Supported protocols (expand as needed)
PROTOCOLS = {
    "101.1": "Online sale 101.1 (4 digit Auth Code)",
    "101.2": "Online sale/Purchase 101.2 (6 digit Auth Code)",
    "101.3": "Online sale 101.3 (6 digit Auth Code)",
    "101.4": "Online sale/Purchase 101.4 (4 & 6 digit Auth Code)",
    "101.5": "Online sale 101.5 (digit Auth Code)",
    "101.6": "Online sale 101.6 Pre-Auth [1:1]",
    "101.7": "Online forced sale 101.7 (4 digit Auth Code)",
    "101.8": "Online sale Pinless 101.8",
    "201.1": "Online sale one step completion 201.1 (6 digit Auth Code)",
    "201.2": "Offline forced sale 201.2 (6 digit Auth Code)",
    "201.3": "Offline sale 201.3 (6 digit Auth Code)",
    "201.4": "Online sale Ticket Only / Phone Order 201.4 (6 digit Auth Code)",
    "201.1b": "Online sale Pre-Auth and completion (1:More) 201.1 (6 digit Auth Code)",
    "100": "Protocol 100",
    "101": "Protocol 101",
    "201": "Protocol 201"
}

class CardTransactionRequest(BaseModel):
    terminal_id: str
    user_id: int
    protocol: str
    card_number: str
    expiry: str
    cvv: str
    auth_code: str
    amount: float
    currency: str

class CardTransactionResponse(BaseModel):
    reference: str
    status: str
    card_masked: str
    protocol: str
    amount: float
    currency: str
    message: str

def mask_card(card_number: str) -> str:
    # Mask all but last 4 digits
    return "**** **** **** " + card_number[-4:]

def iso8583_validate(request: CardTransactionRequest) -> bool:
    # Add real ISO8583 logic/field checks here if needed
    # Example: Check length, Luhn, expiry, protocol, etc.
    if len(request.card_number) < 13 or len(request.card_number) > 19:
        return False
    if not request.protocol in PROTOCOLS:
        return False
    # Add more ISO checks as needed
    return True

@router.post("/process", response_model=CardTransactionResponse)
def process_card_transaction(
    req: CardTransactionRequest,
    db: Session = Depends(get_db)
):
    # Validate ISO8583 fields/protocol
    if not iso8583_validate(req):
        raise HTTPException(status_code=400, detail="Invalid protocol or card details")
    # Mask card for storage
    card_masked = mask_card(req.card_number)
    # Simulate authorization (replace with real bank/issuer/ISO8583 comms)
    # TODO: Integrate real payment gateway/ISO8583 switch
    # Here, we simply accept 4/6 digit auth codes as valid
    if req.protocol.startswith("101") and len(req.auth_code) not in (4, 6):
        return CardTransactionResponse(
            reference="",
            status="Reject",
            card_masked=card_masked,
            protocol=req.protocol,
            amount=req.amount,
            currency=req.currency,
            message="Authorization code invalid for protocol"
        )
    # Save transaction
    ref = f"TXN{secrets.randbelow(10**9):09d}"
    txn = Transaction(
        reference=ref,
        terminal_id=req.terminal_id,
        user_id=req.user_id,
        card_masked=card_masked,
        protocol=req.protocol,
        amount=req.amount,
        currency=req.currency,
        payout_type="",  # to be filled after payout step
        payout_details=None,
        status="Success",
        created_at=datetime.now()
    )
    db.add(txn)
    db.commit()
    return CardTransactionResponse(
        reference=ref,
        status="Success",
        card_masked=card_masked,
        protocol=req.protocol,
        amount=req.amount,
        currency=req.currency,
        message="Transaction authorized"
    )

@router.get("/protocols")
def get_protocols():
    return [{"code": k, "label": v} for k, v in PROTOCOLS.items()]
