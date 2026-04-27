"""Pacote de schemas Pydantic da API."""

from app.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleStatusUpdate,
    CustomerResponse,
    ProfessionalSummaryResponse,
    ScheduleSuggestionRequest,
    ScheduleSuggestionItem,
    ScheduleSuggestionResponse,
)
from app.schemas.customer import CustomerCreate, CustomerRecord, CustomerUpdate
from app.schemas.professional import ProfessionalCreate, ProfessionalResponse, ProfessionalUpdate
from app.schemas.working_hours import WorkingHoursCreate, WorkingHoursResponse
from app.schemas.auth import (
    AuthRegister,
    AuthLogin,
    RefreshTokenRequest,
    TokenResponse,
    AccessTokenResponse,
)

__all__ = [
    "ScheduleCreate",
    "ScheduleResponse",
    "ScheduleStatusUpdate",
    "CustomerResponse",
    "ProfessionalSummaryResponse",
    "ScheduleSuggestionRequest",
    "ScheduleSuggestionItem",
    "ScheduleSuggestionResponse",
    "WorkingHoursCreate",
    "WorkingHoursResponse",
    "CustomerCreate",
    "CustomerRecord",
    "CustomerUpdate",
    "ProfessionalCreate",
    "ProfessionalResponse",
    "ProfessionalUpdate",
    "AuthRegister",
    "AuthLogin",
    "RefreshTokenRequest",
    "TokenResponse",
    "AccessTokenResponse",
]

