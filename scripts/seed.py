"""
Seed script: Creates the initial superadmin user.
Run with: uv run python -m scripts.seed
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import hash_password
from app.core.enums import UserRole

SUPERADMIN_EMAIL = "admin@mikrotik.local"
SUPERADMIN_PASSWORD = "Admin@1234!"  # Change immediately after first login
SUPERADMIN_FIRST_NAME = "Super"
SUPERADMIN_LAST_NAME = "Admin"


async def seed():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == SUPERADMIN_EMAIL))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"[SEED] Superadmin {SUPERADMIN_EMAIL} already exists. Skipping.")
            return

        admin = User(
            email=SUPERADMIN_EMAIL,
            hashed_password=hash_password(SUPERADMIN_PASSWORD),
            first_name=SUPERADMIN_FIRST_NAME,
            last_name=SUPERADMIN_LAST_NAME,
            role=UserRole.SUPERADMIN,
            is_active=True,
            is_email_verified=True,
        )
        db.add(admin)
        await db.commit()
        print(f"[SEED] ✅ Superadmin created: {SUPERADMIN_EMAIL} / {SUPERADMIN_PASSWORD}")
        print("[SEED] ⚠️  Please change the password immediately after first login!")


if __name__ == "__main__":
    asyncio.run(seed())
