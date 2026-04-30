from __future__ import annotations

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.enum.schedule_status import ScheduleStatus
from app.models.company import Company
from app.models.customer import Customer
from app.models.professional import Professional
from app.models.schedule_model import Schedule


class DashboardRepository:
    def __init__(self, db: Session, company_id: int):
        self.db = db
        self.company_id = company_id

    def get_counts(self) -> dict[str, int]:
        schedule_count = (
            self.db.query(func.count(Schedule.id))
            .filter(Schedule.company_id == self.company_id)
            .scalar()
            or 0
        )
        professional_count = (
            self.db.query(func.count(Professional.id))
            .filter(Professional.company_id == self.company_id)
            .scalar()
            or 0
        )
        customer_count = (
            self.db.query(func.count(Customer.id))
            .filter(Customer.company_id == self.company_id)
            .scalar()
            or 0
        )

        return {
            "schedule_count": int(schedule_count),
            "professional_count": int(professional_count),
            "customer_count": int(customer_count),
        }

    def get_average_ticket_amount(self) -> float:
        value = (
            self.db.query(Company.average_ticket_amount)
            .filter(Company.id == self.company_id)
            .scalar()
        )
        if value is None:
            return 100.0
        return float(value)

    def count_completed_schedules(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        query = self.db.query(func.count(Schedule.id)).filter(
            Schedule.company_id == self.company_id,
            Schedule.status == ScheduleStatus.COMPLETED,
        )

        if start_date is not None:
            query = query.filter(Schedule.date >= start_date)
        if end_date is not None:
            query = query.filter(Schedule.date <= end_date)

        return int(query.scalar() or 0)

    def get_revenue_by_professional(
        self,
        average_ticket_amount: float,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, int | float | str | None]]:
        query = (
            self.db.query(
                Schedule.professional_id.label("professional_id"),
                Professional.name.label("professional_name"),
                func.count(Schedule.id).label("completed_schedules"),
            )
            .outerjoin(
                Professional,
                (Professional.id == Schedule.professional_id)
                & (Professional.company_id == self.company_id),
            )
            .filter(
                Schedule.company_id == self.company_id,
                Schedule.status == ScheduleStatus.COMPLETED,
            )
            .group_by(Schedule.professional_id, Professional.name)
            .order_by(func.count(Schedule.id).desc())
        )

        if start_date is not None:
            query = query.filter(Schedule.date >= start_date)
        if end_date is not None:
            query = query.filter(Schedule.date <= end_date)

        rows = query.all()
        result: list[dict[str, int | float | str | None]] = []
        for row in rows:
            completed_schedules = int(row.completed_schedules)
            result.append(
                {
                    "professional_id": row.professional_id,
                    "professional_name": row.professional_name or "Sem profissional definido",
                    "completed_schedules": completed_schedules,
                    "total_revenue": float(completed_schedules * average_ticket_amount),
                }
            )
        return result

    def get_next_schedules(self, limit: int = 5) -> list[Schedule]:
        return (
            self.db.query(Schedule)
            .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
            .filter(Schedule.company_id == self.company_id)
            .order_by(Schedule.date.desc(), Schedule.time.desc())
            .limit(limit)
            .all()
        )
