# SPDX-FileCopyrightText: © Береску Николае
# SPDX-License-Identifier: Proprietary
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.device import Device
from app.models.user import User
from datetime import datetime, timezone

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("")
def list_devices(user_id: int = 1, db: Session = Depends(get_db)):
    """Пока user_id = 1 (заглушка, до внедрения токенов refresh)"""
    devices = db.query(Device).filter(Device.user_id == user_id).all()
    return [
        {"id": d.id, "device_id": d.device_id, "ua": d.ua,
         "created_at": d.created_at, "last_seen_at": d.last_seen_at}
        for d in devices
    ]

@router.post("/revoke")
def revoke_device(device_id: str, user_id: int = 1, db: Session = Depends(get_db)):
    dev = db.query(Device).filter(Device.user_id == user_id, Device.device_id == device_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(dev)
    db.commit()
    return {"detail": f"Device {device_id} revoked"}
