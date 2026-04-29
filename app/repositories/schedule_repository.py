from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models.schedule_model import Schedule
from app.enum.schedule_status import ScheduleStatus


class ScheduleRepository:
    def __init__(self, db: Session, company_id: int):
        self.db = db
        self.company_id = company_id

    def list(self, skip: int = 0, limit: int = 20) -> list[Schedule]:
        return (
            self.db.query(Schedule)
            .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
            .filter(Schedule.company_id == self.company_id)
            .order_by(Schedule.date.desc(), Schedule.time.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get(self, schedule_id: int) -> Schedule | None:
        return (
            self.db.query(Schedule)
            .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
            .filter(Schedule.id == schedule_id, Schedule.company_id == self.company_id)
            .one_or_none()
        )

    def create(
        self,
        customer_id: int,
        professional_id: int | None,
        schedule_date,
        schedule_time,
    ) -> Schedule:
        new_schedule = Schedule(
            customer_id=customer_id,
            company_id=self.company_id,
            professional_id=professional_id,
            date=schedule_date,
            time=schedule_time,
        )
        self.db.add(new_schedule)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
        self.db.refresh(new_schedule)
        return (
            self.db.query(Schedule)
            .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
            .filter(Schedule.id == new_schedule.id, Schedule.company_id == self.company_id)
            .one_or_none()
        )

    def update(
        self,
        schedule_id: int,
        customer_id: int,
        professional_id: int | None,
        schedule_date,
        schedule_time,
    ) -> Schedule | None:
        schedule = (
            self.db.query(Schedule)
            .filter(Schedule.id == schedule_id, Schedule.company_id == self.company_id)
            .one_or_none()
        )
        if not schedule:
            return None
        schedule.customer_id = customer_id
        schedule.professional_id = professional_id
        schedule.date = schedule_date
        schedule.time = schedule_time
        self.db.commit()
        self.db.refresh(schedule)
        return (
            self.db.query(Schedule)
            .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
            .filter(Schedule.id == schedule.id, Schedule.company_id == self.company_id)
            .one_or_none()
        )

    def delete(self, schedule_id: int) -> bool:
        schedule = (
            self.db.query(Schedule)
            .filter(Schedule.id == schedule_id, Schedule.company_id == self.company_id)
            .one_or_none()
        )
        if not schedule:
            return False
        self.db.delete(schedule)
        self.db.commit()
        return True

    def check_conflict(
        self,
        schedule_date,
        schedule_time,
        professional_id: int | None,
        exclude_id: int | None = None,
    ) -> bool:
        active_statuses = (ScheduleStatus.PENDING, ScheduleStatus.CONFIRMED)
        query = self.db.query(Schedule).filter(
            Schedule.company_id == self.company_id,
            Schedule.date == schedule_date,
            Schedule.time == schedule_time,
            Schedule.status.in_(active_statuses),
        )

        if professional_id is None:
            query = query.filter(Schedule.professional_id.is_(None))
        else:
            query = query.filter(Schedule.professional_id == professional_id)

        if exclude_id is not None:
            query = query.filter(Schedule.id != exclude_id)
        return self.db.query(query.exists()).scalar()

    def list_by_customer(self, customer_id: int) -> list[Schedule]:
        return (
            self.db.query(Schedule)
            .filter(Schedule.customer_id == customer_id, Schedule.company_id == self.company_id)
            .order_by(Schedule.date.desc())
            .all()
        )

    def count_active_by_date(self, schedule_date) -> int:
        active_statuses = (ScheduleStatus.PENDING, ScheduleStatus.CONFIRMED)
        return (
            self.db.query(Schedule)
            .filter(
                Schedule.company_id == self.company_id,
                Schedule.date == schedule_date,
                Schedule.status.in_(active_statuses),
            )
            .count()
        )

    def update_status(self, schedule_id: int, new_status) -> Schedule | None:
        schedule = (
            self.db.query(Schedule)
            .filter(Schedule.id == schedule_id, Schedule.company_id == self.company_id)
            .one_or_none()
        )
        if not schedule:
            return None
        schedule.status = new_status
        self.db.commit()
        self.db.refresh(schedule)
        return (
            self.db.query(Schedule)
            .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
            .filter(Schedule.id == schedule.id, Schedule.company_id == self.company_id)
            .one_or_none()
        )
