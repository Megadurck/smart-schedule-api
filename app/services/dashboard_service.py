from __future__ import annotations

from datetime import date, datetime

from fastapi import HTTPException

from app.repositories.dashboard_repository import DashboardRepository


def _parse_date(value: str | None, field_name: str) -> date | None:
    if value is None:
        return None
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Formato inválido para {field_name}. Use DD/MM/YYYY.",
        )


def get_dashboard_insights(
    repository: DashboardRepository,
    start_date: str | None = None,
    end_date: str | None = None,
):
    parsed_start_date = _parse_date(start_date, "start_date")
    parsed_end_date = _parse_date(end_date, "end_date")

    if parsed_start_date and parsed_end_date and parsed_start_date > parsed_end_date:
        raise HTTPException(status_code=400, detail="start_date não pode ser maior que end_date.")

    counts = repository.get_counts()
    average_ticket_amount = repository.get_average_ticket_amount()
    completed_schedules = repository.count_completed_schedules(parsed_start_date, parsed_end_date)
    total_revenue = float(completed_schedules * average_ticket_amount)

    return {
        "start_date": parsed_start_date,
        "end_date": parsed_end_date,
        **counts,
        "average_ticket_amount": average_ticket_amount,
        "completed_schedules": completed_schedules,
        "total_revenue": total_revenue,
        "revenue_by_professional": repository.get_revenue_by_professional(
            average_ticket_amount,
            parsed_start_date,
            parsed_end_date,
        ),
        "next_schedules": repository.get_next_schedules(limit=5),
    }
