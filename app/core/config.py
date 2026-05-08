from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MikroTik Hotspot Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://mikrotik-hotspot-manager.vercel.app",
    ]
    # Database
    DATABASE_URL: str  # asyncpg — used by the app
    SYNC_DATABASE_URL: str  # psycopg2 — used by Alembic only
    BASE_URL: str = "http://localhost:8000"
    # JWT
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@example.com"
    # Upload
    MAX_FILE_SIZE_MB: int = 5
    # Admin Credentials
    SUPERADMIN_EMAIL: str
    SUPERADMIN_PASSWORD: str
    SUPERADMIN_FIRST_NAME: str = "Super"
    SUPERADMIN_LAST_NAME: str = "Admin"
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: str | list) -> list:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
