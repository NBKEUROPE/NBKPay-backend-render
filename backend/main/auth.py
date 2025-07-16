from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from db import get_db
from models.user import User
from config import config
import secrets

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str
    terminal_id: str

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=24)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm="HS256")
    return encoded_jwt

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=req.username, terminal_id=req.terminal_id).first()
    if not user or not bcrypt.verify(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User disabled")
    access_token = create_access_token(
        data={"sub": user.username, "uid": user.id, "admin": user.is_admin, "terminal": user.terminal_id}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# OTP logic (simplified, extend as needed)
@router.post("/request-otp")
def request_otp(username: str = Body(...), terminal_id: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username, terminal_id=terminal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp = secrets.randbelow(1000000)
    user.otp_secret = str(otp).zfill(6)
    db.commit()
    # TODO: send OTP via SMS/email (see notifications.py)
    return {"msg": "OTP sent"}

@router.post("/verify-otp")
def verify_otp(username: str = Body(...), terminal_id: str = Body(...), otp: str = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username, terminal_id=terminal_id).first()
    if not user or user.otp_secret != otp:
        raise HTTPException(status_code=401, detail="Invalid OTP")
    user.otp_secret = None
    db.commit()
    return {"msg": "OTP verified"}

@router.post("/change-password")
def change_password(
    username: str = Body(...),
    terminal_id: str = Body(...),
    old_password: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(username=username, terminal_id=terminal_id).first()
    if not user or not bcrypt.verify(old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.hashed_password = bcrypt.hash(new_password)
    db.commit()
    return {"msg": "Password changed"}

@router.post("/forgot-password")
def forgot_password(
    username: str = Body(...),
    terminal_id: str = Body(...),
    contact: str = Body(...),
    otp: str = Body(None),
    new_password: str = Body(None),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter_by(username=username, terminal_id=terminal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # If OTP and new_password given, verify and reset
    if otp and new_password:
        if user.otp_secret != otp:
            raise HTTPException(status_code=401, detail="Invalid OTP")
        user.hashed_password = bcrypt.hash(new_password)
        user.otp_secret = None
        db.commit()
        return {"msg": "Password reset"}
    # Otherwise, send OTP
    otp_val = secrets.randbelow(1000000)
    user.otp_secret = str(otp_val).zfill(6)
    db.commit()
    # TODO: send OTP via SMS/email (see notifications.py)
    return {"msg": "OTP sent"}

@router.post("/master-reset")
def master_reset(
    username: str = Body(...),
    terminal_id: str = Body(...),
    master_password: str = Body(...),
    db: Session = Depends(get_db)
):
    # Only superadmin can trigger master reset
    if master_password != config.SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid master password")
    user = db.query(User).filter_by(username=username, terminal_id=terminal_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = bcrypt.hash("changeme123")
    db.commit()
    return {"msg": "Password reset to default, please change after login."}
