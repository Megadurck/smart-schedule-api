from pydantic import BaseModel, Field


class CompanyAdminSettingsUpdate(BaseModel):
    display_name: str | None = None
    cancellation_policy: str | None = None
    default_timezone: str = "America/Sao_Paulo"
    reminder_lead_minutes: int = Field(default=120, ge=0, le=10080)


class CompanyAdminSettingsResponse(BaseModel):
    company_id: int
    company_name: str
    display_name: str | None = None
    cancellation_policy: str | None = None
    default_timezone: str
    reminder_lead_minutes: int

    model_config = {"from_attributes": True}
