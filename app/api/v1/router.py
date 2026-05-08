from fastapi import APIRouter

from app.api.v1.routes.shared import profile
from app.api.v1.routes.superadmin import users, vendors, logs, subdomains
from app.api.v1.routes.superadmin import routers as superadmin_routers
from app.api.v1.routes.vendor import routers as vendor_routers
from app.api.v1.routes import auth

api_router = APIRouter(prefix="/api/v1")

# Auth — public + shared
api_router.include_router(auth.router)
# Shared — both roles
api_router.include_router(profile.router)
# Superadmin only
api_router.include_router(vendors.router, prefix="/superadmin")
api_router.include_router(users.router, prefix="/superadmin")
api_router.include_router(superadmin_routers.router, prefix="/superadmin")
api_router.include_router(subdomains.router, prefix="/superadmin")
api_router.include_router(logs.router, prefix="/superadmin")
# Vendor only
api_router.include_router(vendor_routers.router, prefix="/vendor")
