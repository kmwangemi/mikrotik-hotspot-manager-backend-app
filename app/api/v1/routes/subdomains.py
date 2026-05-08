from fastapi import APIRouter, Query

from app.api.v1.dependencies.auth import DB
from app.services import vendor_service

router = APIRouter(prefix="/subdomains", tags=["Subdomains"])


@router.get("/check")
async def check_subdomain(
    db: DB,
    subdomain: str = Query(..., min_length=1, description="The subdomain to check"),
):
    exists = await vendor_service.check_subdomain_exists(db, subdomain)
    return {"exists": exists}
