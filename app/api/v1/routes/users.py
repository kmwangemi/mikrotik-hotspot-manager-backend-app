from fastapi import APIRouter, HTTPException, status, Request
from sqlalchemy import select

from app.api.v1.dependencies.auth import DB, SuperAdminUser, get_client_ip
from app.models.user import User
from app.schemas.user import UserRead, SuperAdminCreate
from app.services.log_service import log_action
from app.core.security import hash_password
from app.core.enums import LogCategory, LogStatus, UserRole

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserRead])
async def list_users(current_user: SuperAdminUser, db: DB):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, current_user: SuperAdminUser, db: DB):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/superadmin", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_superadmin(
    body: SuperAdminCreate,
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    # Check if email exists
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_admin = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        phone=body.phone,
        role=UserRole.SUPERADMIN,
        is_email_verified=True,
    )
    db.add(new_admin)
    await db.flush()

    await log_action(
        db,
        action="Created Superadmin User",
        category=LogCategory.USER_MANAGEMENT,
        status=LogStatus.SUCCESS,
        details=f"New superadmin created: {new_admin.email}",
        user=current_user,
        ip_address=ip,
        metadata={"new_user_id": new_admin.id},
    )
    return new_admin


@router.patch("/{user_id}/deactivate", response_model=UserRead)
async def deactivate_user(
    user_id: str,
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    user.is_active = False
    await db.flush()
    await log_action(
        db,
        action="Deactivated User Account",
        category=LogCategory.USER_MANAGEMENT,
        status=LogStatus.WARNING,
        details=f"User {user.email} deactivated",
        user=current_user,
        ip_address=ip,
        metadata={"target_user_id": user_id},
    )
    return user


@router.patch("/{user_id}/activate", response_model=UserRead)
async def activate_user(
    user_id: str,
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    await db.flush()
    await log_action(
        db,
        action="Activated User Account",
        category=LogCategory.USER_MANAGEMENT,
        status=LogStatus.SUCCESS,
        details=f"User {user.email} activated",
        user=current_user,
        ip_address=ip,
        metadata={"target_user_id": user_id},
    )
    return user
