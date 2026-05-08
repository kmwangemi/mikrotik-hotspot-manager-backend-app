from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.core.security import decode_token
from app.core.enums import TokenType, UserRole, Permission, ROLE_PERMISSIONS

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    payload = decode_token(credentials.credentials, TokenType.ACCESS)
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Contact support.",
        )
    # Attach token claims to the user object so routes can use them
    # without extra DB queries
    user.token_subdomain = payload.get("subdomain")
    user.token_jti = payload.get("jti")
    return user


async def get_current_superadmin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superadmin access required",
        )
    return current_user


async def get_current_vendor(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != UserRole.VENDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vendor access required",
        )
    return current_user


def require_permission(permission: Permission):
    """Factory to create a permission-checking dependency."""

    async def check_permission(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        allowed = ROLE_PERMISSIONS.get(current_user.role, [])
        if permission not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required",
            )
        return current_user
    return check_permission


def get_client_ip(request: Request) -> Optional[str]:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> Optional[str]:
    return request.headers.get("User-Agent")


# Convenience aliases
CurrentUser = Annotated[User, Depends(get_current_user)]
SuperAdminUser = Annotated[User, Depends(get_current_superadmin)]
VendorUser = Annotated[User, Depends(get_current_vendor)]
DB = Annotated[AsyncSession, Depends(get_db)]
