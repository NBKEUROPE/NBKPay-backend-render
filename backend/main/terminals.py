from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from db import get_db
from models.terminal import Terminal

router = APIRouter()

@router.get("/")
def list_terminals(db: Session = Depends(get_db)):
    return db.query(Terminal).all()

@router.post("/create")
def create_terminal(terminal_id: str = Body(...), name: str = Body(None), location: str = Body(None), db: Session = Depends(get_db)):
    if db.query(Terminal).filter_by(terminal_id=terminal_id).first():
        raise HTTPException(status_code=400, detail="Terminal exists")
    t = Terminal(terminal_id=terminal_id, name=name, location=location)
    db.add(t)
    db.commit()
    return {"msg": "Terminal created"}

@router.post("/status")
def set_terminal_status(terminal_id: str = Body(...), is_active: bool = Body(...), db: Session = Depends(get_db)):
    t = db.query(Terminal).filter_by(terminal_id=terminal_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Terminal not found")
    t.is_active = is_active
    db.commit()
    return {"msg": "Terminal updated"}
