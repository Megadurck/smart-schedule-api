from datetime import date

from pydantic import BaseModel

from app.schemas.schedule import ScheduleResponse


class RevenueByProfessionalItem(BaseModel):
    professional_id: int | None
    professional_name: str
    completed_schedules: int
    total_revenue: float


class DashboardInsightsResponse(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    schedule_count: int
    professional_count: int
    customer_count: int
    average_ticket_amount: float
    completed_schedules: int
    total_revenue: float
    revenue_by_professional: list[RevenueByProfessionalItem]
    next_schedules: list[ScheduleResponse]
