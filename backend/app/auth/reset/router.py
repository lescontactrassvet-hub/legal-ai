from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.auth.reset.schemas import (
    ResetStartRequest,
    ResetStartResponse,
    ResetVerifyRequest,
    ResetVerifyResponse,
    ResetCompleteRequest,
    ResetCompleteResponse,
)
from app.auth.reset.service import (
    start_reset,
    verify_reset_token,
    complete_reset,
)

router = APIRouter(prefix="/auth", tags=["auth-reset"])


@router.post("/reset-start", response_model=ResetStartResponse)
def reset_start(payload: ResetStartRequest, db: Session = Depends(get_db)):
    return start_reset(db, payload)


@router.post("/reset-verify", response_model=ResetVerifyResponse)
def reset_verify(payload: ResetVerifyRequest, db: Session = Depends(get_db)):
    return verify_reset_token(db, payload)


@router.post("/reset-complete", response_model=ResetCompleteResponse)
def reset_complete(payload: ResetCompleteRequest, db: Session = Depends(get_db)):
    return complete_reset(db, payload)
