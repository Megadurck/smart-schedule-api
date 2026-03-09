from datetime import time, timedelta
from sqlalchemy.orm import Session
from app.models.working_hours_model import WorkingHours
from app.enum.weekday import Weekday


def set_working_hours(
    db: Session,
    weekday: Weekday | int,
    start_time: time,
    end_time: time,
    slot_duration_minutes: int = 30,
    lunch_start: time | None = None,
    lunch_end: time | None = None,
):
    # Validações de domínio
    if start_time >= end_time:
        raise ValueError("start_time must be before end_time")

    if lunch_start and lunch_end:
        if lunch_start >= lunch_end:
            raise ValueError("Invalid lunch interval")

        if lunch_start <= start_time or lunch_end >= end_time:
            raise ValueError("Lunch must be inside working hours")
    
    working_hours = (
        db.query(WorkingHours)
        .filter(WorkingHours.weekday == weekday)
        .first()
    )

    if working_hours:
        working_hours.start_time = start_time
        working_hours.end_time = end_time
        working_hours.slot_duration_minutes = slot_duration_minutes
        working_hours.lunch_start = lunch_start
        working_hours.lunch_end = lunch_end
        working_hours.is_active = True
    else:
        working_hours = WorkingHours(
            weekday= int(weekday),
            start_time=start_time,
            end_time=end_time,
            slot_duration_minutes=slot_duration_minutes,
            lunch_start=lunch_start,
            lunch_end=lunch_end,
            is_active=True
        )
        db.add(working_hours)

    db.commit()
    db.refresh(working_hours)

    return working_hours


def list_working_hours(db: Session):

    return (
        db.query(WorkingHours)
        .order_by(WorkingHours.weekday)
        .all()
    )

def is_within_working_hours(
    db: Session,
    weekday: Weekday | int,
    schedule_time: time
) -> bool:

    working_hours = (
        db.query(WorkingHours)
        .filter(
            WorkingHours.weekday == weekday,
            WorkingHours.is_active == True
        )
        .first()
    )

    if not working_hours:
        return False

    # Verificar se está dentro do horário de almoço
    if working_hours.lunch_start and working_hours.lunch_end:
        if working_hours.lunch_start <= schedule_time < working_hours.lunch_end:
            return False

    return working_hours.start_time <= schedule_time <= working_hours.end_time


def calculate_available_slots(db: Session, weekday: int) -> dict:
    """Calcula quantos slots de atendimento estão disponíveis no dia"""
    working_hours = (
        db.query(WorkingHours)
        .filter(
            WorkingHours.weekday == weekday,
            WorkingHours.is_active == True
        )
        .first()
    )

    if not working_hours:
        return {
            "weekday": int(weekday),
            "available_slots": 0,
            "total_time_minutes": 0,
            "lunch_duration_minutes": 0,
        }

    # Convertendo time para minutos desde o início do dia
    def time_to_minutes(t: time) -> int:
        return t.hour * 60 + t.minute

    start_minutes = time_to_minutes(working_hours.start_time)
    end_minutes = time_to_minutes(working_hours.end_time)
    
    # Calcular tempo de pausa de almoço
    lunch_duration = 0
    if working_hours.lunch_start and working_hours.lunch_end:
        lunch_start_min = time_to_minutes(working_hours.lunch_start)
        lunch_end_min = time_to_minutes(working_hours.lunch_end)
        lunch_duration = lunch_end_min - lunch_start_min

    # Tempo total disponível
    total_time = end_minutes - start_minutes - lunch_duration
    
    # Calcular slots disponíveis
    slot_duration = working_hours.slot_duration_minutes
    available_slots = total_time // slot_duration if slot_duration > 0 else 0

    return {
        "weekday": int(weekday),
        "start_time": str(working_hours.start_time),
        "end_time": str(working_hours.end_time),
        "lunch_start": str(working_hours.lunch_start) if working_hours.lunch_start else None,
        "lunch_end": str(working_hours.lunch_end) if working_hours.lunch_end else None,
        "slot_duration_minutes": slot_duration,
        "total_available_minutes": total_time,
        "total_lunch_minutes": lunch_duration,
        "available_slots": available_slots,
    }