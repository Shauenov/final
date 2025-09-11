from fastapi import APIRouter
from app.modules.user.user_router import user_router
from app.modules.auth.auth_router import auth_router
from app.modules.device.device_router import device_router

api_router = APIRouter()

api_router.include_router(user_router)
api_router.include_router(device_router)
api_router.include_router(auth_router)
