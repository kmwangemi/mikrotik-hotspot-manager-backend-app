from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

from app.api.v1.dependencies.auth import DB, CurrentUser, get_client_ip
from app.core.config import settings
from app.core.enums import LogCategory, LogStatus
from app.schemas.profile import ProfileUpdate
from app.schemas.user import UserRead
from app.services import user_service
from app.services.cloudinary_service import (
    delete_profile_picture,
    upload_profile_picture,
)
from app.services.log_service import log_action

router = APIRouter(prefix="/profile", tags=["Profile"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


@router.get("", response_model=UserRead)
async def get_profile(current_user: CurrentUser):
    return current_user


@router.patch("", response_model=UserRead)
async def update_profile(
    body: ProfileUpdate,
    current_user: CurrentUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    user = await user_service.update_profile(
        db,
        current_user,
        body,
    )
    await log_action(
        db,
        action="Updated Profile",
        category=LogCategory.PROFILE,
        status=LogStatus.SUCCESS,
        details="User and vendor profile updated",
        user=current_user,
        ip_address=ip,
    )
    return user


@router.post("/picture", response_model=UserRead)
async def upload_profile_picture_route(
    current_user: CurrentUser,
    db: DB,
    request: Request,
    file: UploadFile = File(...),
):
    ip = get_client_ip(request)
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}",
        )
    content = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size is {settings.MAX_FILE_SIZE_MB}MB",
        )
    try:
        url = await upload_profile_picture(content, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}",
        )
    user = await user_service.update_profile_picture(db, current_user, url)
    await log_action(
        db,
        action="Updated Profile Picture",
        category=LogCategory.PROFILE,
        status=LogStatus.SUCCESS,
        details="Profile picture uploaded to Cloudinary",
        user=current_user,
        ip_address=ip,
    )
    return user


@router.delete("/picture", response_model=UserRead)
async def remove_profile_picture(
    current_user: CurrentUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    try:
        await delete_profile_picture(current_user.id)
    except Exception:
        pass  # Don't block the DB update if Cloudinary delete fails
    user = await user_service.update_profile_picture(db, current_user, None)
    await log_action(
        db,
        action="Removed Profile Picture",
        category=LogCategory.PROFILE,
        status=LogStatus.SUCCESS,
        details="Profile picture removed from Cloudinary",
        user=current_user,
        ip_address=ip,
    )
    return user
