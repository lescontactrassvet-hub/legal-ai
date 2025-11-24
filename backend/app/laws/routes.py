from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db import get_db
from app.laws.models import Law
from app.laws.schemas import LawCreate, LawRead, LawSearchResult
from app.laws.sync import sync_all_sources
from app.laws.fetch_full_text import fetch_full_text_batch

router = APIRouter(
    prefix="/laws",
    tags=["laws"],
)


@router.post("/", response_model=LawRead, status_code=status.HTTP_201_CREATED)
def create_law(payload: LawCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(Law)
        .filter(
            Law.source == payload.source,
            Law.external_id == payload.external_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Запись уже существует",
        )

    law = Law(**payload.model_dump())
    db.add(law)
    db.commit()
    db.refresh(law)
    return law


@router.get("/{law_id}", response_model=LawRead)
def get_law(law_id: int, db: Session = Depends(get_db)):
    law = db.query(Law).filter(Law.id == law_id).first()
    if not law:
        raise HTTPException(status_code=404, detail="Не найдено")
    return law


@router.get("/search", response_model=List[LawSearchResult])
def search_laws(
    q: str = Query(...),
    country: Optional[str] = None,
    law_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    pattern = f"%{q}%"

    query = db.query(Law)

    if country:
        query = query.filter(Law.country == country)
    if law_type:
        query = query.filter(Law.law_type == law_type)

    query = query.filter(
        (Law.title.ilike(pattern)) | (Law.summary.ilike(pattern))
    )

    return (
        query.order_by(Law.date_effective.desc().nullslast())
        .limit(limit)
        .all()
    )


@router.get("/today", response_model=List[LawSearchResult])
def laws_today(country: str = "RU", db: Session = Depends(get_db)):
    today = date.today()

    return (
        db.query(Law)
        .filter(
            Law.country == country,
            Law.date_effective == today,
        )
        .order_by(Law.date_published.desc().nullslast())
        .all()
    )


@router.post("/sync-all", status_code=status.HTTP_202_ACCEPTED)
def sync_all_laws(background_tasks: BackgroundTasks):
    """
    Ручной запуск полной синхронизации:
      1) загрузка законов из всех источников;
      2) дозагрузка полного текста для части записей.

    Использовать только из доверенной админки / Postman.
    """
    background_tasks.add_task(sync_all_sources)
    background_tasks.add_task(fetch_full_text_batch, 200)
    return {"detail": "Синхронизация запущена в фоне"}
