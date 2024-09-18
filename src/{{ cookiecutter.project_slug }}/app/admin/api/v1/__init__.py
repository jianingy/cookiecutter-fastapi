from fastapi import APIRouter
from .admin_users import router as admin_users_router

router = APIRouter(tags=['Administration APIs'])
router.include_router(admin_users_router)
