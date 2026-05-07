from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.vendor import Vendor
from app.models.user import User
from app.core.security import hash_password
from app.core.enums import UserRole, VendorStatus
from app.schemas.vendor import VendorCreate, VendorUpdate, VendorStatusUpdate


async def create_vendor(db: AsyncSession, data: VendorCreate) -> Tuple[Vendor, User]:
    vendor = Vendor(
        business_name=data.business_name,
        business_email=data.business_email,
        business_phone=data.business_phone,
        business_address=data.business_address,
        status=VendorStatus.ACTIVE,
    )
    db.add(vendor)
    await db.flush()

    admin = User(
        email=data.admin.email,
        hashed_password=hash_password(data.admin.password),
        first_name=data.admin.first_name,
        last_name=data.admin.last_name,
        phone=data.admin.phone,
        role=UserRole.VENDOR,
        is_email_verified=True,
        vendor_id=vendor.id,
    )
    db.add(admin)
    await db.flush()
    return vendor, admin


async def get_vendor(db: AsyncSession, vendor_id: str) -> Optional[Vendor]:
    result = await db.execute(
        select(Vendor)
        .options(selectinload(Vendor.admin_user))
        .where(Vendor.id == vendor_id)
    )
    return result.scalar_one_or_none()


async def get_vendors_paginated(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    search: Optional[str] = None,
    status: Optional[VendorStatus] = None,
) -> Tuple[list[Vendor], int]:
    query = select(Vendor)
    count_query = select(func.count()).select_from(Vendor)

    if search:
        like = f"%{search}%"
        query = query.where(Vendor.business_name.ilike(like) | Vendor.business_email.ilike(like))
        count_query = count_query.where(
            Vendor.business_name.ilike(like) | Vendor.business_email.ilike(like)
        )
    if status:
        query = query.where(Vendor.status == status)
        count_query = count_query.where(Vendor.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(Vendor.created_at.desc()).offset(offset).limit(page_size)
    )
    vendors = result.scalars().all()
    return list(vendors), total


async def update_vendor(db: AsyncSession, vendor: Vendor, data: VendorUpdate) -> Vendor:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(vendor, field, value)
    await db.flush()
    return vendor


async def update_vendor_status(
    db: AsyncSession, vendor: Vendor, data: VendorStatusUpdate
) -> Vendor:
    vendor.status = data.status
    vendor.suspension_reason = data.suspension_reason
    await db.flush()
    return vendor


async def delete_vendor(db: AsyncSession, vendor: Vendor) -> None:
    await db.delete(vendor)
    await db.flush()
