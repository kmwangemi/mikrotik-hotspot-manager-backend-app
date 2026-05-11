import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.core.enums import VendorStatus


class VendorAdminInfo(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str


class VendorCreate(BaseModel):
    # Business info
    business_name: str
    business_email: EmailStr
    business_phone_number: Optional[str] = None
    subdomain: str
    referral_code: Optional[str] = None
    business_address: Optional[str] = None
    # Admin user info
    admin: VendorAdminInfo

    @field_validator("subdomain")
    @classmethod
    def validate_subdomain(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) < 3:
            raise ValueError("Subdomain must be at least 3 characters")
        if len(v) > 50:
            raise ValueError("Subdomain must not exceed 50 characters")
        if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", v):
            raise ValueError(
                "Subdomain may only contain lowercase letters, numbers, and hyphens, "
                "and cannot start or end with a hyphen"
            )
        if "--" in v:
            raise ValueError("Subdomain cannot contain consecutive hyphens")
        return v


class VendorUpdate(BaseModel):
    business_name: Optional[str] = None
    business_email: Optional[str] = None
    business_phone_number: Optional[str] = None
    subdomain: Optional[str] = None
    referral_code: Optional[str] = None
    business_address: Optional[str] = None
    logo_url: Optional[str] = None


class VendorStatusUpdate(BaseModel):
    status: VendorStatus
    suspension_reason: Optional[str] = None


class VendorRead(BaseModel):
    id: str
    business_name: str
    business_email: str
    business_phone_number: Optional[str] = None
    subdomain: str
    referral_code: Optional[str] = None
    business_address: Optional[str] = None
    logo_url: Optional[str] = None
    status: VendorStatus
    suspension_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VendorWithAdmin(VendorRead):
    admin_user: Optional[dict] = None

    model_config = {"from_attributes": True}


class PaginatedVendors(BaseModel):
    items: list[VendorRead]
    total: int
    page: int
    page_size: int
    total_pages: int
