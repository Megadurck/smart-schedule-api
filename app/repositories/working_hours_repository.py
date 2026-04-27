from __future__ import annotations

from datetime import time
from sqlalchemy.orm import Session

from app.models.working_hours_model import WorkingHours
from app.enum.weekday import Weekday


class WorkingHoursRepository:
    def __init__(self, db: Session, company_id: int):
        self.db = db
        self.company_id = company_id

    def get_by_weekday(self, weekday: Weekday | int) -> WorkingHours | None:
        return (
            self.db.query(WorkingHours)
            .filter(
                WorkingHours.company_id == self.company_id,
                WorkingHours.weekday == weekday,
            )
            .one_or_none()
        )

    def get_active_by_weekday(self, weekday: Weekday | int) -> WorkingHours | None:
        return (
            self.db.query(WorkingHours)
            .filter(
                WorkingHours.company_id == self.company_id,
                WorkingHours.weekday == weekday,
                WorkingHours.is_active == True,
            )
            .one_or_none()
        )

    def list(self) -> list[WorkingHours]:
        return (
            self.db.query(WorkingHours)
            .filter(WorkingHours.company_id == self.company_id)
            .order_by(WorkingHours.weekday)
            .all()
        )

    def list_active(self) -> list[WorkingHours]:
        return (
            self.db.query(WorkingHours)
            .filter(
                WorkingHours.company_id == self.company_id,
                WorkingHours.is_active == True,
            )
            .all()
        )

    def upsert(
        self,
        weekday: Weekday | int,
        start_time: time,
        end_time: time,
        slot_duration_minutes: int = 30,
        lunch_start: time | None = None,
        lunch_end: time | None = None,
    ) -> WorkingHours:
        wh = self.get_by_weekday(weekday)
        if wh:
            wh.start_time = start_time
            wh.end_time = end_time
            wh.slot_duration_minutes = slot_duration_minutes
            wh.lunch_start = lunch_start
            wh.lunch_end = lunch_end
            wh.is_active = True
        else:
            wh = WorkingHours(
                company_id=self.company_id,
                weekday=int(weekday),
                start_time=start_time,
                end_time=end_time,
                slot_duration_minutes=slot_duration_minutes,
                lunch_start=lunch_start,
                lunch_end=lunch_end,
                is_active=True,
            )
            self.db.add(wh)
        self.db.commit()
        self.db.refresh(wh)
        return wh
