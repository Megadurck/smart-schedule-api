from fastapi import APIRouter

from .routers.health import router as health_router
from .routers.schedule import router as schedule_router
from .routers.working_hours import router as working_hours_router
from .routers.auth import router as auth_router
from .routers.customers import router as customers_router
from .routers.professionals import router as professionals_router
from .routers.company_admin import router as company_admin_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(schedule_router)
api_router.include_router(working_hours_router)
api_router.include_router(auth_router)
api_router.include_router(customers_router)
api_router.include_router(professionals_router)
api_router.include_router(company_admin_router)