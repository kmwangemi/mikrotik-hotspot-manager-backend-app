from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.core.enums import UserRole, VendorStatus

# ── Vendor (nested inside user profile) ───────────────────────────────────────


class VendorProfile(BaseModel):
    id: str
    business_name: str
    business_email: str
    business_phone_number: str
    subdomain: str
    business_address: Optional[str] = None
    logo_url: Optional[str] = None
    status: VendorStatus
    referral_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── User ───────────────────────────────────────────────────────────────────────


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.VENDOR

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    profile_picture_url: Optional[str] = None


class UserRead(UserBase):
    id: str
    role: UserRole
    is_active: bool
    is_email_verified: bool
    profile_picture_url: Optional[str] = None
    vendor_id: Optional[str] = None
    # Nested vendor profile — populated when user is a VENDOR
    vendor: Optional[VendorProfile] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserPublic(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: UserRole
    profile_picture_url: Optional[str] = None
    vendor_id: Optional[str] = None
    vendor: Optional[VendorProfile] = None

    model_config = {"from_attributes": True}


class SuperAdminCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
