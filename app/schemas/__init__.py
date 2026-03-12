"""Pacote de schemas Pydantic da API."""

from app.schemas.schedule import ScheduleCreate
from app.schemas.working_hours import WorkingHoursCreate

__all__ = ["ScheduleCreate", "WorkingHoursCreate"]

