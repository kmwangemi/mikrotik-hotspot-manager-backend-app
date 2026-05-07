from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.enums import TokenType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


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
    to_encode.update({"exp": expire, "type": token_type.value})
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
    payload = jwt.decode(token, secret, algorithms=[settings.ALGORITHM])
    if payload.get("type") != token_type.value:
        raise JWTError("Invalid token type")
    return payload


def generate_otp() -> str:
    import random
    return str(random.randint(100000, 999999))
