from __future__ import annotations
import uuid
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.db.base import TimestampMixin
from app.core.enums import RouterStatus

if TYPE_CHECKING:
    from app.models.vendor import Vendor


class Router(Base, TimestampMixin):
    __tablename__ = "routers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    vendor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=8728, nullable=False)
    api_username: Mapped[str] = mapped_column(String(100), nullable=False)
    api_password: Mapped[str] = mapped_column(String(255), nullable=False)  # stored encrypted
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[RouterStatus] = mapped_column(
        SAEnum(RouterStatus, name="router_status"),
        nullable=False,
        default=RouterStatus.OFFLINE,
    )
    last_seen_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relations
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="routers")
