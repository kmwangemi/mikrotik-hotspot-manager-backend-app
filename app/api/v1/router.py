from fastapi import APIRouter
from app.api.v1.routes import auth, vendors, routers, profile, logs, users

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(vendors.router)
api_router.include_router(routers.router)
api_router.include_router(profile.router)
api_router.include_router(logs.router)
api_router.include_router(users.router)
