from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.core.enums import RouterStatus


class RouterCreate(BaseModel):
    name: str
    ip_address: str
    port: int = 8728
    api_username: str
    api_password: str
    location: Optional[str] = None
    notes: Optional[str] = None


class RouterUpdate(BaseModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    api_username: Optional[str] = None
    api_password: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[RouterStatus] = None


class RouterRead(BaseModel):
    id: str
    vendor_id: str
    name: str
    ip_address: str
    port: int
    api_username: str
    location: Optional[str] = None
    notes: Optional[str] = None
    status: RouterStatus
    last_seen_at: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedRouters(BaseModel):
    items: list[RouterRead]
    total: int
    page: int
    page_size: int
    total_pages: int
