from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.enums import TokenType, UserRole
from app.core.config import settings


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


async def create_token_pair(
    db: AsyncSession,
    user: User,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Tuple[str, str]:
    data = {"sub": user.id, "role": user.role.value, "email": user.email}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)

    # Persist refresh token
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(db_token)
    await db.flush()
    return access_token, refresh_token


async def refresh_access_token(
    db: AsyncSession, refresh_token: str
) -> Tuple[str, User]:
    try:
        payload = decode_token(refresh_token, TokenType.REFRESH)
    except JWTError:
        raise ValueError("Invalid or expired refresh token")

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False,
        )
    )
    db_token = result.scalar_one_or_none()
    if not db_token:
        raise ValueError("Refresh token not found or revoked")
    if db_token.expires_at < datetime.now(timezone.utc):
        raise ValueError("Refresh token expired")

    user_result = await db.execute(select(User).where(User.id == payload["sub"]))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise ValueError("User not found or inactive")

    data = {"sub": user.id, "role": user.role.value, "email": user.email}
    new_access_token = create_access_token(data)
    return new_access_token, user


async def revoke_refresh_token(db: AsyncSession, refresh_token: str) -> bool:
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    db_token = result.scalar_one_or_none()
    if db_token:
        db_token.is_revoked = True
        await db.flush()
        return True
    return False


async def revoke_all_user_tokens(db: AsyncSession, user_id: str) -> None:
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        )
    )
    tokens = result.scalars().all()
    for token in tokens:
        token.is_revoked = True
    await db.flush()
