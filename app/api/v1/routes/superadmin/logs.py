import csv
import io
import math
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, func, select

from app.api.v1.dependencies.auth import DB, SuperAdminUser
from app.core.enums import LogCategory, LogStatus
from app.models.activity_log import ActivityLog
from app.schemas.activity_log import PaginatedLogs

router = APIRouter(prefix="/logs", tags=["Superadmin - Activity Logs"])


@router.get("", response_model=PaginatedLogs)
async def list_logs(
    current_user: SuperAdminUser,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[LogCategory] = Query(None),
    log_status: Optional[LogStatus] = Query(None, alias="status"),
):
    filters = []
    if search:
        like = f"%{search}%"
        filters.append(
            ActivityLog.action.ilike(like)
            | ActivityLog.user_email.ilike(like)
            | ActivityLog.user_name.ilike(like)
            | ActivityLog.details.ilike(like)
            | ActivityLog.ip_address.ilike(like)
        )
    if category:
        filters.append(ActivityLog.category == category)
    if log_status:
        filters.append(ActivityLog.status == log_status)
    count_query = select(func.count()).select_from(ActivityLog)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()
    query = select(ActivityLog)
    if filters:
        query = query.where(and_(*filters))
    query = query.order_by(ActivityLog.created_at.desc())
    offset = (page - 1) * page_size
    result = await db.execute(query.offset(offset).limit(page_size))
    logs = result.scalars().all()
    return PaginatedLogs(
        items=logs,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/export")
async def export_logs(
    current_user: SuperAdminUser,
    db: DB,
    category: Optional[LogCategory] = Query(None),
    log_status: Optional[LogStatus] = Query(None, alias="status"),
):
    """Export logs as CSV."""
    filters = []
    if category:
        filters.append(ActivityLog.category == category)
    if log_status:
        filters.append(ActivityLog.status == log_status)
    query = select(ActivityLog).order_by(ActivityLog.created_at.desc())
    if filters:
        query = query.where(and_(*filters))
    result = await db.execute(query)
    logs = result.scalars().all()
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "id",
            "timestamp",
            "user_name",
            "user_email",
            "action",
            "category",
            "status",
            "details",
            "ip_address",
        ],
    )
    writer.writeheader()
    for log in logs:
        writer.writerow(
            {
                "id": log.id,
                "timestamp": log.created_at.isoformat(),
                "user_name": log.user_name or "",
                "user_email": log.user_email or "",
                "action": log.action,
                "category": log.category.value,
                "status": log.status.value,
                "details": log.details or "",
                "ip_address": log.ip_address or "",
            }
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=activity_logs.csv"},
    )
