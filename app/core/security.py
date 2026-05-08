import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import settings
from app.core.enums import TokenType

# ── Password hashing ───────────────────────────────────────────

password_hash = PasswordHash([Argon2Hasher()])


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


# ── JWT tokens ─────────────────────────────────────────────────


def create_token(
    data: dict[str, Any],
    token_type: TokenType,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    if token_type == TokenType.ACCESS:
        secret = settings.SECRET_KEY
        default_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        secret = settings.REFRESH_SECRET_KEY
        default_expire = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + (expires_delta or default_expire)
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "jti": str(uuid.uuid4()),
            "type": token_type.value,
        }
    )
    return jwt.encode(to_encode, secret, algorithm=settings.ALGORITHM)


def create_access_token(data: dict[str, Any]) -> str:
    return create_token(data, TokenType.ACCESS)


def create_refresh_token(data: dict[str, Any]) -> str:
    return create_token(data, TokenType.REFRESH)


def decode_token(token: str, token_type: TokenType) -> dict[str, Any]:
    secret = (
        settings.SECRET_KEY
        if token_type == TokenType.ACCESS
        else settings.REFRESH_SECRET_KEY
    )
    try:
        payload = jwt.decode(token, secret, algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if payload.get("type") != token_type.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type: expected '{token_type.value}'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def verify_access_token(token: str) -> Optional[str]:
    """Soft verify — returns 'sub' or None. No exception raised."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
        if payload.get("type") != TokenType.ACCESS.value:
            return None
        return payload.get("sub")
    except jwt.InvalidTokenError:
        return None


# ── OTP ────────────────────────────────────────────────────────


def generate_otp() -> str:
    # secrets.randbelow is cryptographically secure, unlike random.randint
    return str(900000 + secrets.randbelow(900000)).zfill(6)
