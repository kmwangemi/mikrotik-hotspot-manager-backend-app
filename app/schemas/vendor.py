from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.core.enums import VendorStatus


class VendorAdminInfo(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
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


class VendorUpdate(BaseModel):
    business_name: Optional[str] = None
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
