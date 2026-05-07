"""
Seed script: Creates the initial superadmin user.
Run with: uv run python -m scripts.seed
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.core.config import settings
from app.core.enums import UserRole
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.user import User


async def seed():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == settings.SUPERADMIN_EMAIL)
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(
                f"[SEED] Superadmin {settings.SUPERADMIN_EMAIL} already exists. Skipping."
            )
            return
        admin = User(
            email=settings.SUPERADMIN_EMAIL,
            hashed_password=hash_password(settings.SUPERADMIN_PASSWORD),
            first_name=settings.SUPERADMIN_FIRST_NAME,
            last_name=settings.SUPERADMIN_LAST_NAME,
            role=UserRole.SUPERADMIN,
            is_active=True,
            is_email_verified=True,
        )
        db.add(admin)
        await db.commit()
        print(f"[SEED] ✅ Superadmin created: {settings.SUPERADMIN_EMAIL}")
        print("[SEED] ⚠️  Please change the password immediately after first login!")


if __name__ == "__main__":
    asyncio.run(seed())
