from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EmailVerificationStatus
from app.db.base import TimestampMixin
from app.db.session import Base


class EmailVerification(Base, TimestampMixin):
    __tablename__ = "email_verifications"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    otp_code: Mapped[str] = mapped_column(String(10), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[EmailVerificationStatus] = mapped_column(
        SAEnum(
            EmailVerificationStatus,
            name="email_verification_status",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=EmailVerificationStatus.PENDING,
        nullable=False,
    )
