import math

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.api.v1.dependencies.auth import (
    DB,
    SuperAdminUser,
    get_client_ip,
)
from app.core.enums import LogCategory, LogStatus, VendorStatus
from app.schemas.vendor import (
    PaginatedVendors,
    VendorCreate,
    VendorRead,
    VendorStatusUpdate,
    VendorUpdate,
)
from app.services import vendor_service
from app.services.log_service import log_action

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    body: VendorCreate,
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    try:
        vendor, admin = await vendor_service.create_vendor(db, body)
    except Exception as e:
        await log_action(
            db,
            action="Create Vendor Failed",
            category=LogCategory.VENDOR_MANAGEMENT,
            status=LogStatus.ERROR,
            details=str(e),
            user=current_user,
            ip_address=ip,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await log_action(
        db,
        action="Created New Vendor",
        category=LogCategory.VENDOR_MANAGEMENT,
        status=LogStatus.SUCCESS,
        details=f"Vendor '{vendor.business_name}' created with admin {admin.email}",
        user=current_user,
        ip_address=ip,
        metadata={"vendor_id": vendor.id},
    )
    return vendor


@router.get("", response_model=PaginatedVendors)
async def list_vendors(
    current_user: SuperAdminUser,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    status: VendorStatus = Query(None),
):
    vendors, total = await vendor_service.get_vendors_paginated(
        db, page=page, page_size=page_size, search=search, status=status
    )
    return PaginatedVendors(
        items=vendors,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{vendor_id}", response_model=VendorRead)
async def get_vendor(vendor_id: str, current_user: SuperAdminUser, db: DB):
    vendor = await vendor_service.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )
    return vendor


@router.patch("/{vendor_id}", response_model=VendorRead)
async def update_vendor(
    vendor_id: str,
    body: VendorUpdate,
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    vendor = await vendor_service.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )
    vendor = await vendor_service.update_vendor(db, vendor, body)
    await log_action(
        db,
        action="Updated Vendor",
        category=LogCategory.VENDOR_MANAGEMENT,
        status=LogStatus.SUCCESS,
        details=f"Vendor '{vendor.business_name}' updated",
        user=current_user,
        ip_address=ip,
        metadata={"vendor_id": vendor_id},
    )
    return vendor


@router.patch("/{vendor_id}/status", response_model=VendorRead)
async def update_vendor_status(
    vendor_id: str,
    body: VendorStatusUpdate,
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    vendor = await vendor_service.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )
    vendor = await vendor_service.update_vendor_status(db, vendor, body)
    action_label = (
        "Suspended Vendor Account"
        if body.status == VendorStatus.SUSPENDED
        else f"Updated Vendor Status to {body.status.value}"
    )
    log_status = (
        LogStatus.WARNING
        if body.status == VendorStatus.SUSPENDED
        else LogStatus.SUCCESS
    )
    await log_action(
        db,
        action=action_label,
        category=LogCategory.VENDOR_MANAGEMENT,
        status=log_status,
        details=body.suspension_reason or f"Status changed to {body.status.value}",
        user=current_user,
        ip_address=ip,
        metadata={"vendor_id": vendor_id, "new_status": body.status.value},
    )
    return vendor


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(
    vendor_id: str,
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    vendor = await vendor_service.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )
    name = vendor.business_name
    await vendor_service.delete_vendor(db, vendor)
    await log_action(
        db,
        action="Deleted Vendor",
        category=LogCategory.VENDOR_MANAGEMENT,
        status=LogStatus.WARNING,
        details=f"Vendor '{name}' permanently deleted",
        user=current_user,
        ip_address=ip,
        metadata={"vendor_id": vendor_id},
    )
