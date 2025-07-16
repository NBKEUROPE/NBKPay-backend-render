from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from pydantic import BaseModel
from typing import List
from jose import jwt, JWTError
from config import config

router = APIRouter()

def get_current_user(token: str = Body(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        user = db.query(User).filter_by(id=payload["uid"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class UserOut(BaseModel):
    id: int
    username: str
    is_admin: bool
    is_superadmin: bool
    is_active: bool
    terminal_id: str

    class Config:
        orm_mode = True

@router.get("/", response_model=List[UserOut])
def list_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin and not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(User).all()

@router.post("/toggle-active")
def toggle_user_active(user_id: int = Body(...), is_active: bool = Body(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin and not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Not authorized")
    u = db.query(User).filter_by(id=user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.is_active = is_active
    db.commit()
    return {"msg": f"User {'enabled' if is_active else 'disabled'}"}
