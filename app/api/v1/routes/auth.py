from fastapi import APIRouter, HTTPException, Request, status

from app.api.v1.dependencies.auth import DB, CurrentUser, get_client_ip, get_user_agent
from app.core.enums import LogCategory, LogStatus
from app.schemas.auth import (
    AccessTokenResponse,
    ChangePasswordRequest,
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    SendOTPRequest,
    SendOTPResponse,
    TokenResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
)
from app.schemas.user import UserPublic
from app.services import auth_service, email_service, user_service
from app.services.log_service import log_action

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db: DB):
    ip = get_client_ip(request)
    ua = get_user_agent(request)
    user = await auth_service.authenticate_user(db, body.email, body.password)
    if not user:
        await log_action(
            db,
            action="Failed Login Attempt",
            category=LogCategory.AUTH,
            status=LogStatus.ERROR,
            details=f"Failed login for {body.email}",
            user_email=body.email,
            ip_address=ip,
            user_agent=ua,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token, refresh_token = await auth_service.create_token_pair(db, user, ip, ua)
    await log_action(
        db,
        action="User Login",
        category=LogCategory.AUTH,
        status=LogStatus.SUCCESS,
        details=f"Successful login",
        user=user,
        ip_address=ip,
        user_agent=ua,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        user_id=user.id,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(body: RefreshTokenRequest, db: DB):
    try:
        access_token, user = await auth_service.refresh_access_token(
            db, body.refresh_token
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    body: RefreshTokenRequest, current_user: CurrentUser, db: DB, request: Request
):
    ip = get_client_ip(request)
    await auth_service.revoke_refresh_token(db, body.refresh_token)
    await log_action(
        db,
        action="User Logout",
        category=LogCategory.AUTH,
        status=LogStatus.SUCCESS,
        user=current_user,
        ip_address=ip,
    )
    return LogoutResponse(message="Logged out successfully")


@router.post("/logout-all", response_model=LogoutResponse)
async def logout_all(current_user: CurrentUser, db: DB, request: Request):
    ip = get_client_ip(request)
    await auth_service.revoke_all_user_tokens(db, current_user.id)
    await log_action(
        db,
        action="User Logout All Sessions",
        category=LogCategory.AUTH,
        status=LogStatus.SUCCESS,
        user=current_user,
        ip_address=ip,
    )
    return LogoutResponse(message="All sessions revoked")


@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(body: SendOTPRequest, db: DB):
    await email_service.send_verification_otp(db, body.email)
    return SendOTPResponse(
        message="Verification code sent to your email",
        email=body.email,
    )


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(body: VerifyOTPRequest, db: DB):
    verified = await email_service.verify_otp(db, body.email, body.otp_code)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code",
        )
    return VerifyOTPResponse(verified=True, message="Email verified successfully")


@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest, current_user: CurrentUser, db: DB, request: Request
):
    ip = get_client_ip(request)
    success = await user_service.update_user_password(
        db, current_user, body.current_password, body.new_password
    )
    if not success:
        await log_action(
            db,
            action="Password Change Failed",
            category=LogCategory.AUTH,
            status=LogStatus.ERROR,
            user=current_user,
            ip_address=ip,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    await log_action(
        db,
        action="Password Changed",
        category=LogCategory.AUTH,
        status=LogStatus.SUCCESS,
        user=current_user,
        ip_address=ip,
    )
    return {"message": "Password updated successfully"}


@router.get("/me", response_model=UserPublic)
async def get_me(current_user: CurrentUser):
    return current_user
