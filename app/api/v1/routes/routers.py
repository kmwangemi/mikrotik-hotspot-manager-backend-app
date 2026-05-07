import math
from fastapi import APIRouter, HTTPException, status, Request, Query

from app.api.v1.dependencies.auth import DB, CurrentUser, VendorUser, SuperAdminUser, get_client_ip
from app.schemas.router import RouterCreate, RouterUpdate, RouterRead, PaginatedRouters
from app.services import router_service
from app.services.log_service import log_action
from app.core.enums import LogCategory, LogStatus, UserRole

router = APIRouter(prefix="/routers", tags=["Routers"])


def _assert_router_access(current_user, router_obj):
    """Vendors can only access their own vendor's routers."""
    if current_user.role == UserRole.VENDOR and router_obj.vendor_id != current_user.vendor_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.post("", response_model=RouterRead, status_code=status.HTTP_201_CREATED)
async def create_router(
    body: RouterCreate,
    current_user: VendorUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    if not current_user.vendor_id:
        raise HTTPException(status_code=400, detail="User is not linked to a vendor")

    r = await router_service.create_router(db, current_user.vendor_id, body)
    await log_action(
        db,
        action="Added New Router",
        category=LogCategory.ROUTER_MANAGEMENT,
        status=LogStatus.SUCCESS,
        details=f"Router '{r.name}' ({r.ip_address}) added",
        user=current_user,
        ip_address=ip,
        metadata={"router_id": r.id},
    )
    return r


@router.get("", response_model=PaginatedRouters)
async def list_routers(
    current_user: CurrentUser,
    db: DB,
    vendor_id: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    # Vendors always see only their own; superadmin can filter by vendor_id
    target_vendor_id = (
        current_user.vendor_id
        if current_user.role == UserRole.VENDOR
        else vendor_id
    )
    if not target_vendor_id:
        raise HTTPException(status_code=400, detail="vendor_id is required")

    routers, total = await router_service.get_routers_by_vendor(
        db, target_vendor_id, page=page, page_size=page_size
    )
    return PaginatedRouters(
        items=routers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{router_id}", response_model=RouterRead)
async def get_router(router_id: str, current_user: CurrentUser, db: DB):
    r = await router_service.get_router(db, router_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Router not found")
    _assert_router_access(current_user, r)
    return r


@router.patch("/{router_id}", response_model=RouterRead)
async def update_router(
    router_id: str,
    body: RouterUpdate,
    current_user: VendorUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    r = await router_service.get_router(db, router_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Router not found")
    _assert_router_access(current_user, r)

    r = await router_service.update_router(db, r, body)
    await log_action(
        db,
        action="Updated Router Configuration",
        category=LogCategory.ROUTER_MANAGEMENT,
        status=LogStatus.SUCCESS,
        details=f"Router '{r.name}' updated",
        user=current_user,
        ip_address=ip,
        metadata={"router_id": router_id},
    )
    return r


@router.delete("/{router_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_router(
    router_id: str,
    current_user: VendorUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    r = await router_service.get_router(db, router_id)
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Router not found")
    _assert_router_access(current_user, r)

    name = r.name
    await router_service.delete_router(db, r)
    await log_action(
        db,
        action="Deleted Router",
        category=LogCategory.ROUTER_MANAGEMENT,
        status=LogStatus.WARNING,
        details=f"Router '{name}' permanently deleted",
        user=current_user,
        ip_address=ip,
        metadata={"router_id": router_id},
    )
