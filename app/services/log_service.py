from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.core.enums import LogCategory, LogStatus


async def log_action(
    db: AsyncSession,
    *,
    action: str,
    category: LogCategory,
    status: LogStatus = LogStatus.SUCCESS,
    details: Optional[str] = None,
    user: Optional[User] = None,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    user_name: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> ActivityLog:
    """
    Persist an activity log entry to the database.
    Can accept a User object or raw user identifiers.
    """
    if user:
        user_id = user.id
        user_email = user.email
        user_name = user.full_name

    entry = ActivityLog(
        action=action,
        category=category,
        status=status,
        details=details,
        user_id=user_id,
        user_email=user_email,
        user_name=user_name,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata_=metadata,
    )
    db.add(entry)
    await db.flush()  # get ID without full commit
    return entry
