import os
import uuid
import aiofiles
from fastapi import APIRouter, HTTPException, status, Request, UploadFile, File
from fastapi.responses import JSONResponse

from app.api.v1.dependencies.auth import DB, CurrentUser, get_client_ip
from app.schemas.user import UserRead, UserUpdate
from app.services import user_service
from app.services.log_service import log_action
from app.core.enums import LogCategory, LogStatus
from app.core.config import settings

router = APIRouter(prefix="/profile", tags=["Profile"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


@router.get("", response_model=UserRead)
async def get_profile(current_user: CurrentUser):
    return current_user


@router.patch("", response_model=UserRead)
async def update_profile(
    body: UserUpdate,
    current_user: CurrentUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    user = await user_service.update_user_profile(db, current_user, body)
    await log_action(
        db,
        action="Updated Profile",
        category=LogCategory.PROFILE,
        status=LogStatus.SUCCESS,
        details="Profile information updated",
        user=current_user,
        ip_address=ip,
    )
    return user


@router.post("/picture", response_model=UserRead)
async def upload_profile_picture(
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

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size is {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "profile_pictures")
    os.makedirs(upload_dir, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{current_user.id}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_dir, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    url = f"/static/profile_pictures/{filename}"
    user = await user_service.update_profile_picture(db, current_user, url)

    await log_action(
        db,
        action="Updated Profile Picture",
        category=LogCategory.PROFILE,
        status=LogStatus.SUCCESS,
        details="Profile picture uploaded and updated",
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
    user = await user_service.update_profile_picture(db, current_user, None)
    await log_action(
        db,
        action="Removed Profile Picture",
        category=LogCategory.PROFILE,
        status=LogStatus.SUCCESS,
        user=current_user,
        ip_address=ip,
    )
    return user
