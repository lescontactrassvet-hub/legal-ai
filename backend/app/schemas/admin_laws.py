from typing import List, Optional
from pydantic import BaseModel


class LawSourceStatus(BaseModel):
    id: int
    name: str
    type: str
    parser: str
    base_url: Optional[str]
    is_active: bool

    last_status: Optional[str] = None
    last_started_at: Optional[str] = None
    last_finished_at: Optional[str] = None
    last_total_items: Optional[int] = None
    last_processed_items: Optional[int] = None
    last_inserted_items: Optional[int] = None
    last_failed_items: Optional[int] = None


class LawUpdateLogEntry(BaseModel):
    id: int
    source_id: Optional[int]
    status: str
    message: Optional[str]
    details: Optional[str]
    total_items: Optional[int]
    processed_items: Optional[int]
    inserted_items: Optional[int]
    failed_items: Optional[int]
    started_at: str
    finished_at: Optional[str]


class LawUpdateLogPage(BaseModel):
    items: List[LawUpdateLogEntry]
    total: int
    limit: int
    offset: int

