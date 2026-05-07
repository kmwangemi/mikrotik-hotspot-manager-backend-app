from __future__ import annotations
import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Enum as SAEnum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.db.base import TimestampMixin
from app.core.enums import UserRole

if TYPE_CHECKING:
    from app.models.vendor import Vendor
    from app.models.refresh_token import RefreshToken
    from app.models.activity_log import ActivityLog


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), nullable=False, default=UserRole.VENDOR
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Vendor relation (vendor users link to a vendor)
    vendor_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("vendors.id", ondelete="SET NULL"), nullable=True
    )
    vendor: Mapped[Optional["Vendor"]] = relationship("Vendor", back_populates="admin_user")

    # Tokens
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    # Logs
    activity_logs: Mapped[List["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
