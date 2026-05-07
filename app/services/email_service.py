from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.models.email_verification import EmailVerification
from app.core.security import generate_otp
from app.core.enums import EmailVerificationStatus
from app.core.config import settings


async def send_verification_otp(db: AsyncSession, email: str) -> str:
    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Invalidate old codes for this email
    result = await db.execute(
        select(EmailVerification).where(
            EmailVerification.email == email,
            EmailVerification.status == EmailVerificationStatus.PENDING,
        )
    )
    old_codes = result.scalars().all()
    for code in old_codes:
        code.status = EmailVerificationStatus.EXPIRED

    # Create new verification record
    verification = EmailVerification(
        email=email,
        otp_code=otp,
        expires_at=expires_at,
        status=EmailVerificationStatus.PENDING,
    )
    db.add(verification)
    await db.flush()

    # Send email (fire and forget – log failures)
    try:
        _send_email(email, otp)
    except Exception as e:
        print(f"[EMAIL] Failed to send OTP to {email}: {e}")

    return otp  # Return in dev; in prod, don't expose


async def verify_otp(db: AsyncSession, email: str, otp_code: str) -> bool:
    result = await db.execute(
        select(EmailVerification).where(
            EmailVerification.email == email,
            EmailVerification.otp_code == otp_code,
            EmailVerification.status == EmailVerificationStatus.PENDING,
            EmailVerification.is_used == False,
        )
    )
    verification = result.scalar_one_or_none()
    if not verification:
        return False
    if verification.expires_at < datetime.now(timezone.utc):
        verification.status = EmailVerificationStatus.EXPIRED
        await db.flush()
        return False

    verification.is_used = True
    verification.status = EmailVerificationStatus.VERIFIED
    await db.flush()
    return True


def _send_email(to_email: str, otp: str) -> None:
    if not settings.SMTP_USER:
        print(f"[EMAIL DEV] OTP for {to_email}: {otp}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Your Verification Code"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email

    html = f"""
    <html><body>
    <h2>Email Verification</h2>
    <p>Your one-time verification code is:</p>
    <h1 style="letter-spacing:4px;">{otp}</h1>
    <p>This code expires in 10 minutes. Do not share it with anyone.</p>
    </body></html>
    """
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
