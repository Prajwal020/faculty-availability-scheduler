from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.departments import router as departments_router
from app.api.v1.users import router as users_router
from app.api.v1.admin import router as admin_router
from app.api.v1.availability import router as availability_router
from app.api.v1.leave import router as leave_router
from app.api.v1.appointments import router as appointments_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(departments_router)
api_router.include_router(users_router)
api_router.include_router(admin_router)
api_router.include_router(availability_router)
api_router.include_router(leave_router)
api_router.include_router(appointments_router)
