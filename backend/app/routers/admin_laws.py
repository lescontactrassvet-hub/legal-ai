from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.admin_laws import (
    LawSourceStatus,
    LawUpdateLogEntry,
    LawUpdateLogPage,
)
from app.dependencies import get_db

router = APIRouter(
    prefix="/admin/laws",
    tags=["admin:laws"],
)


@router.get("/sources", response_model=List[LawSourceStatus])
def list_sources_with_status(db: Session = Depends(get_db)) -> List[LawSourceStatus]:
    sql = text(
        """
        WITH last_logs AS (
            SELECT * FROM (
                SELECT
                    l.id,
                    l.source_id,
                    l.status,
                    l.message,
                    l.details,
                    l.total_items,
                    l.processed_items,
                    l.inserted_items,
                    l.failed_items,
                    l.started_at,
                    l.finished_at
                FROM law_update_log l
                JOIN (
                    SELECT source_id, MAX(id) AS max_id
                    FROM law_update_log
                    GROUP BY source_id
                ) x ON x.source_id = l.source_id AND x.max_id = l.id
            )
        )
        SELECT
            s.id AS source_id,
            s.name,
            s.type,
            s.parser,
            s.base_url,
            s.is_active,
            ll.status,
            ll.started_at,
            ll.finished_at,
            ll.total_items,
            ll.processed_items,
            ll.inserted_items,
            ll.failed_items
        FROM law_sources s
        LEFT JOIN last_logs ll ON ll.source_id = s.id
        ORDER BY s.id
        """
    )

    rows = db.execute(sql).mappings().all()

    return [
        LawSourceStatus(
            id=row["source_id"],
            name=row["name"],
            type=row["type"],
            parser=row["parser"],
            base_url=row["base_url"],
            is_active=bool(row["is_active"]),
            last_status=row["status"],
            last_started_at=row["started_at"],
            last_finished_at=row["finished_at"],
            last_total_items=row["total_items"],
            last_processed_items=row["processed_items"],
            last_inserted_items=row["inserted_items"],
            last_failed_items=row["failed_items"],
        )
        for row in rows
    ]


@router.get("/update-log", response_model=LawUpdateLogPage)
def list_update_log(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    source_id: Optional[int] = Query(None),
) -> LawUpdateLogPage:

    params = {"limit": limit, "offset": offset}

    if source_id is None:
        where = "1=1"
    else:
        where = "source_id = :source_id"
        params["source_id"] = source_id

    count_sql = text(f"SELECT COUNT(*) FROM law_update_log WHERE {where}")
    total = db.execute(count_sql, params).scalar_one()

    sql = text(
        f"""
        SELECT
            id,
            source_id,
            status,
            message,
            details,
            total_items,
            processed_items,
            inserted_items,
            failed_items,
            started_at,
            finished_at
        FROM law_update_log
        WHERE {where}
        ORDER BY started_at DESC
        LIMIT :limit OFFSET :offset
        """
    )

    rows = db.execute(sql, params).mappings().all()

    items = [
        LawUpdateLogEntry(
            id=row["id"],
            source_id=row["source_id"],
            status=row["status"],
            message=row["message"],
            details=row["details"],
            total_items=row["total_items"],
            processed_items=row["processed_items"],
            inserted_items=row["inserted_items"],
            failed_items=row["failed_items"],
            started_at=row["started_at"],
            finished_at=row["finished_at"],
        )
        for row in rows
    ]

    return LawUpdateLogPage(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/sources/{source_id}/update-log", response_model=LawUpdateLogPage)
def list_update_log_for_source(
    source_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return list_update_log(
        db=db,
        limit=limit,
        offset=offset,
        source_id=source_id,
    )

