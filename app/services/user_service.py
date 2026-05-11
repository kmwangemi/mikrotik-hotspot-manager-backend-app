from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.profile import ProfileUpdate


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def update_profile(
    db: AsyncSession,
    current_user: User,
    data: ProfileUpdate,
) -> User:

    # -----------------------------
    # Update User Fields
    # -----------------------------
    if data.user:
        user_data = data.user.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        for field, value in user_data.items():
            setattr(current_user, field, value)
    # -----------------------------
    # Update Vendor Fields
    # -----------------------------
    if data.vendor:
        if not current_user.vendor:
            raise ValueError("User does not belong to a vendor")
        vendor_data = data.vendor.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )
        for field, value in vendor_data.items():
            setattr(current_user.vendor, field, value)
    await db.commit()
    await db.refresh(
        current_user,
        attribute_names=["vendor"],
    )
    return current_user


async def update_user_password(
    db: AsyncSession, user: User, current_password: str, new_password: str
) -> bool:
    if not verify_password(current_password, user.hashed_password):
        return False
    user.hashed_password = hash_password(new_password)
    await db.flush()
    return True


async def update_profile_picture(
    db: AsyncSession, user: User, url: Optional[str]
) -> User:
    user.profile_picture_url = url
    await db.flush()
    return user


async def deactivate_user(db: AsyncSession, user: User) -> User:
    user.is_active = False
    await db.flush()
    return user
