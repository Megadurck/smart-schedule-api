from datetime import time

from app.repositories.working_hours_repository import WorkingHoursRepository
from app.enum.weekday import Weekday


def set_working_hours(
    repo: WorkingHoursRepository,
    weekday: Weekday | int,
    start_time: time,
    end_time: time,
    slot_duration_minutes: int = 30,
    lunch_start: time | None = None,
    lunch_end: time | None = None,
):
    if start_time >= end_time:
        raise ValueError("start_time must be before end_time")
    if lunch_start and lunch_end:
        if lunch_start >= lunch_end:
            raise ValueError("Invalid lunch interval")
        if lunch_start <= start_time or lunch_end >= end_time:
            raise ValueError("Lunch must be inside working hours")
    return repo.upsert(weekday, start_time, end_time, slot_duration_minutes, lunch_start, lunch_end)


def list_working_hours(repo: WorkingHoursRepository):
    return repo.list()


def is_within_working_hours(
    repo: WorkingHoursRepository,
    weekday: Weekday | int,
    schedule_time: time,
) -> bool:
    wh = repo.get_active_by_weekday(weekday)
    if not wh:
        return False
    if wh.lunch_start and wh.lunch_end:
        if wh.lunch_start <= schedule_time < wh.lunch_end:
            return False
    return wh.start_time <= schedule_time <= wh.end_time


def calculate_available_slots(repo: WorkingHoursRepository, weekday: int) -> dict:
    wh = repo.get_active_by_weekday(weekday)
    if not wh:
        return {
            "weekday": int(weekday),
            "available_slots": 0,
            "total_time_minutes": 0,
            "lunch_duration_minutes": 0,
        }

    def time_to_minutes(t: time) -> int:
        return t.hour * 60 + t.minute

    start_minutes = time_to_minutes(wh.start_time)
    end_minutes = time_to_minutes(wh.end_time)
    lunch_duration = 0
    if wh.lunch_start and wh.lunch_end:
        lunch_duration = time_to_minutes(wh.lunch_end) - time_to_minutes(wh.lunch_start)

    total_time = end_minutes - start_minutes - lunch_duration
    slot_duration = wh.slot_duration_minutes
    available_slots = total_time // slot_duration if slot_duration > 0 else 0

    return {
        "weekday": int(weekday),
        "start_time": str(wh.start_time),
        "end_time": str(wh.end_time),
        "lunch_start": str(wh.lunch_start) if wh.lunch_start else None,
        "lunch_end": str(wh.lunch_end) if wh.lunch_end else None,
        "slot_duration_minutes": slot_duration,
        "total_available_minutes": total_time,
        "total_lunch_minutes": lunch_duration,
        "available_slots": available_slots,
    }