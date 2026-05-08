import math

from fastapi import APIRouter, HTTPException, Query, status

from app.api.v1.dependencies.auth import DB, VendorUser
from app.schemas.router import PaginatedRouters, RouterRead
from app.services import router_service

router = APIRouter(prefix="/routers", tags=["Vendor - Routers"])


@router.get("", response_model=PaginatedRouters)
async def list_routers(
    current_user: VendorUser,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    if not current_user.vendor_id:
        raise HTTPException(status_code=400, detail="User is not linked to a vendor")
    print("current_user--->", current_user)
    routers, total = await router_service.get_routers_by_vendor(
        db, current_user.vendor_id, page=page, page_size=page_size
    )
    return PaginatedRouters(
        items=routers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{router_id}", response_model=RouterRead)
async def get_router(router_id: str, current_user: VendorUser, db: DB):
    r = await router_service.get_router(db, router_id)
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Router not found"
        )
    # Ensure vendor can only see their own routers
    if r.vendor_id != current_user.vendor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    return r
