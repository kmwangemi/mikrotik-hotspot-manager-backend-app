from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.router import Router
from app.schemas.router import RouterCreate, RouterUpdate
from app.core.enums import RouterStatus


async def create_router(db: AsyncSession, vendor_id: str, data: RouterCreate) -> Router:
    router = Router(
        vendor_id=vendor_id,
        name=data.name,
        ip_address=data.ip_address,
        port=data.port,
        api_username=data.api_username,
        api_password=data.api_password,  # TODO: encrypt in production
        location=data.location,
        notes=data.notes,
        status=RouterStatus.OFFLINE,
    )
    db.add(router)
    await db.flush()
    return router


async def get_router(db: AsyncSession, router_id: str) -> Optional[Router]:
    result = await db.execute(select(Router).where(Router.id == router_id))
    return result.scalar_one_or_none()


async def get_routers_by_vendor(
    db: AsyncSession,
    vendor_id: str,
    page: int = 1,
    page_size: int = 10,
) -> Tuple[list[Router], int]:
    count_result = await db.execute(
        select(func.count()).select_from(Router).where(Router.vendor_id == vendor_id)
    )
    total = count_result.scalar_one()
    offset = (page - 1) * page_size
    result = await db.execute(
        select(Router)
        .where(Router.vendor_id == vendor_id)
        .order_by(Router.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    return list(result.scalars().all()), total


async def update_router(db: AsyncSession, router: Router, data: RouterUpdate) -> Router:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(router, field, value)
    await db.flush()
    return router


async def delete_router(db: AsyncSession, router: Router) -> None:
    await db.delete(router)
    await db.flush()
