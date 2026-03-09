from fastapi import APIRouter

from .routers.health import router as health_router
from .routers.schedule import router as schedule_router
from .routers.working_hours import router as working_hours_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(schedule_router)
api_router.include_router(working_hours_router)