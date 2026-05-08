import math

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.api.v1.dependencies.auth import DB, SuperAdminUser, get_client_ip
from app.core.enums import LogCategory, LogStatus
from app.schemas.router import PaginatedRouters, RouterCreate, RouterRead, RouterUpdate
from app.services import router_service
from app.services.log_service import log_action

router = APIRouter(prefix="/routers", tags=["Superadmin - Routers"])


@router.post("", response_model=RouterRead, status_code=status.HTTP_201_CREATED)
async def create_router(
    body: RouterCreate,
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    # vendor_id comes from the request body, not from the superadmin user
    r = await router_service.create_router(db, body.vendor_id, body)
    await log_action(
        db,
        action="Added New Router",
        category=LogCategory.ROUTER_MANAGEMENT,
        status=LogStatus.SUCCESS,
        details=f"Router '{r.name}' ({r.ip_address}) added",
        user=current_user,
        ip_address=ip,
        metadata={"router_id": r.id, "vendor_id": body.vendor_id},
    )
    return r


@router.get("", response_model=PaginatedRouters)
async def list_routers(
    current_user: SuperAdminUser,
    db: DB,
    vendor_id: str = Query(None, description="Filter routers by vendor"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    routers, total = await router_service.get_routers_by_vendor(
        db, vendor_id, page=page, page_size=page_size
    )
    return PaginatedRouters(
        items=routers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{router_id}", response_model=RouterRead)
async def get_router(router_id: str, current_user: SuperAdminUser, db: DB):
    r = await router_service.get_router(db, router_id)
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Router not found"
        )
    return r


@router.patch("/{router_id}", response_model=RouterRead)
async def update_router(
    router_id: str,
    body: RouterUpdate,
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    r = await router_service.get_router(db, router_id)
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Router not found"
        )
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
    current_user: SuperAdminUser,
    db: DB,
    request: Request,
):
    ip = get_client_ip(request)
    r = await router_service.get_router(db, router_id)
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Router not found"
        )
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
