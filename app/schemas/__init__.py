"""Pacote de schemas Pydantic da API."""

from app.schemas.schedule import ScheduleCreate, ScheduleResponse, ClientResponse
from app.schemas.working_hours import WorkingHoursCreate, WorkingHoursResponse

__all__ = [
    "ScheduleCreate",
    "ScheduleResponse",
    "ClientResponse",
    "WorkingHoursCreate",
    "WorkingHoursResponse",
]

