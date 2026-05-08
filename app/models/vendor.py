from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import VendorStatus
from app.db.base import TimestampMixin
from app.db.session import Base

if TYPE_CHECKING:
    from app.models.router import Router
    from app.models.user import User


class Vendor(Base, TimestampMixin):
    __tablename__ = "vendors"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Business info
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    business_phone_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False, index=True
    )
    subdomain: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    referral_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    business_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[VendorStatus] = mapped_column(
        SAEnum(
            VendorStatus,
            name="vendor_status",
            values_callable=lambda x: [e.value for e in x],
            nullable=False,
            default=VendorStatus.PENDING,
        )
    )
    suspension_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Admin user (the vendor's primary admin)
    admin_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="vendor", uselist=False
    )
    # Routers
    routers: Mapped[List["Router"]] = relationship(
        "Router", back_populates="vendor", cascade="all, delete-orphan"
    )
