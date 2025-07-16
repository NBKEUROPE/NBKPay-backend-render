# ...existing imports and router...

@router.delete("/delete")
def delete_terminal(terminal_id: str = Body(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmin allowed")
    t = db.query(Terminal).filter_by(terminal_id=terminal_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Terminal not found")
    db.delete(t)
    db.commit()
    return {"msg": "Terminal deleted"}

@router.post("/edit")
def edit_terminal(
    terminal_id: str = Body(...),
    name: str = Body(None),
    location: str = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Only superadmin allowed")
    t = db.query(Terminal).filter_by(terminal_id=terminal_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Terminal not found")
    if name:
        t.name = name
    if location:
        t.location = location
    db.commit()
    return {"msg": "Terminal updated"}
