from datetime import datetime, time

from app.repositories.schedule_repository import ScheduleRepository
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


def _time_to_minutes(value: time) -> int:
    return value.hour * 60 + value.minute


def _parse_date(value: str):
    return datetime.strptime(value, "%d/%m/%Y").date()


def calculate_available_slots_for_date(
    repo: WorkingHoursRepository,
    schedule_repo: ScheduleRepository,
    date_str: str,
) -> dict:
    requested_date = _parse_date(date_str)
    weekday = requested_date.weekday()
    wh = repo.get_active_by_weekday(weekday)

    if not wh:
        return {
            "date": date_str,
            "weekday": int(weekday),
            "available_slots": 0,
            "total_available_minutes": 0,
            "lunch_duration_minutes": 0,
            "slot_duration_minutes": 0,
        }

    start_minutes = _time_to_minutes(wh.start_time)
    end_minutes = _time_to_minutes(wh.end_time)
    lunch_duration = 0
    if wh.lunch_start and wh.lunch_end:
        lunch_duration = _time_to_minutes(wh.lunch_end) - _time_to_minutes(wh.lunch_start)

    total_time = end_minutes - start_minutes - lunch_duration
    slot_duration = wh.slot_duration_minutes
    total_slots = total_time // slot_duration if slot_duration > 0 else 0
    booked_slots = schedule_repo.count_active_by_date(requested_date)
    available_slots = max(total_slots - booked_slots, 0)
    remaining_available_minutes = available_slots * slot_duration if slot_duration > 0 else 0

    return {
        "date": date_str,
        "weekday": int(weekday),
        "start_time": str(wh.start_time),
        "end_time": str(wh.end_time),
        "lunch_start": str(wh.lunch_start) if wh.lunch_start else None,
        "lunch_end": str(wh.lunch_end) if wh.lunch_end else None,
        "slot_duration_minutes": slot_duration,
        "total_available_minutes": remaining_available_minutes,
        "lunch_duration_minutes": lunch_duration,
        "total_lunch_minutes": lunch_duration,
        "total_slots": total_slots,
        "booked_slots": booked_slots,
        "available_slots": available_slots,
    }