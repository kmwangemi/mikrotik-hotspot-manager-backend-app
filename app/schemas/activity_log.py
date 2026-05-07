from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.core.enums import LogCategory, LogStatus


class ActivityLogCreate(BaseModel):
    action: str
    category: LogCategory
    status: LogStatus = LogStatus.SUCCESS
    details: Optional[str] = None
    metadata_: Optional[dict] = None


class ActivityLogRead(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    category: LogCategory
    status: LogStatus
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata_: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedLogs(BaseModel):
    items: list[ActivityLogRead]
    total: int
    page: int
    page_size: int
    total_pages: int
