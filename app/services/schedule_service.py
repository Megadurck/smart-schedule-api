from collections import defaultdict
from datetime import datetime, time, date as date_type, timedelta

from fastapi import HTTPException

from app.models.working_hours_model import WorkingHours


def parse_date_time(date_str: str, time_str: str):
    """Converte strings para objetos ``date`` e ``time``.

    Levanta uma ``HTTPException`` com status 400 caso o formato esteja errado.
    """
    try:
        schedule_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        schedule_time = time.fromisoformat(time_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de data ou hora inválido. Use DD/MM/YYYY para data e HH:MM:SS para hora.",
        )

    return schedule_date, schedule_time


# ---------------------------------------------------------------------------
# auxiliares (helpers)
# ---------------------------------------------------------------------------

def _is_within_working_hours(working_hours_repo, schedule_date: date_type, schedule_time: time) -> bool:
    from app.services import working_hours_service
    return working_hours_service.is_within_working_hours(
        working_hours_repo,
        schedule_date.weekday(),
        schedule_time,
    )


def _get_professional_or_none(professional_repo, professional_id: int | None):
    if professional_id is None:
        return None
    professional = professional_repo.get(professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional nao encontrado")
    return professional


# ---------------------------------------------------------------------------
# Operações de Negócio (usando ScheduleBundle)
# ---------------------------------------------------------------------------

def list_schedules(bundle):
    return bundle.schedules.list()


def get_schedule(bundle, schedule_id: int):
    schedule = bundle.schedules.get(schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return schedule


def create_schedule(
    bundle,
    customer_name: str,
    date_str: str,
    time_str: str,
    professional_id: int | None = None,
):
    schedule_date, schedule_time = parse_date_time(date_str, time_str)

    if bundle.schedules.check_conflict(schedule_date, schedule_time):
        raise HTTPException(status_code=409, detail="Horário já ocupado")

    if not _is_within_working_hours(bundle.working_hours, schedule_date, schedule_time):
        raise HTTPException(
            status_code=422,
            detail="Horário fora do funcionamento. Verifique os horários de trabalho disponíveis.",
        )

    customer = bundle.customers.find_or_create(customer_name)
    professional = _get_professional_or_none(bundle.professionals, professional_id)

    return bundle.schedules.create(
        customer.id,
        professional.id if professional else None,
        schedule_date,
        schedule_time,
    )


def update_schedule(
    bundle,
    schedule_id: int,
    customer_name: str,
    date_str: str,
    time_str: str,
    professional_id: int | None = None,
):
    schedule_date, schedule_time = parse_date_time(date_str, time_str)

    if bundle.schedules.check_conflict(schedule_date, schedule_time, exclude_id=schedule_id):
        raise HTTPException(status_code=409, detail="Horário já ocupado")

    if not _is_within_working_hours(bundle.working_hours, schedule_date, schedule_time):
        raise HTTPException(
            status_code=422,
            detail="Horário fora do funcionamento. Verifique os horários de trabalho disponíveis.",
        )

    customer = bundle.customers.find_or_create(customer_name)
    professional = _get_professional_or_none(bundle.professionals, professional_id)

    schedule = bundle.schedules.update(
        schedule_id,
        customer.id,
        professional.id if professional else None,
        schedule_date,
        schedule_time,
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return schedule


def delete_schedule(bundle, schedule_id: int):
    deleted = bundle.schedules.delete(schedule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return {"detail": "Agendamento deletado"}


def _parse_optional_start_date(start_date: str | None) -> date_type:
    if not start_date:
        return datetime.now().date()

    try:
        return datetime.strptime(start_date, "%d/%m/%Y").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido para start_date. Use DD/MM/YYYY.",
        )


def _time_to_minutes(value: time) -> int:
    return value.hour * 60 + value.minute


def _minutes_to_time(value: int) -> time:
    return time(hour=value // 60, minute=value % 60)


def _build_daily_slots(working_hours: WorkingHours) -> list[time]:
    if working_hours.slot_duration_minutes <= 0:
        return []

    start = _time_to_minutes(working_hours.start_time)
    end = _time_to_minutes(working_hours.end_time)
    lunch_start = _time_to_minutes(working_hours.lunch_start) if working_hours.lunch_start else None
    lunch_end = _time_to_minutes(working_hours.lunch_end) if working_hours.lunch_end else None

    slots: list[time] = []
    current = start
    while current <= end:
        in_lunch_break = (
            lunch_start is not None
            and lunch_end is not None
            and lunch_start <= current < lunch_end
        )
        if not in_lunch_break:
            slots.append(_minutes_to_time(current))

        current += working_hours.slot_duration_minutes

    return slots


def suggest_schedules(
    bundle,
    customer_name: str,
    start_date: str | None = None,
    limit: int = 3,
    search_days: int = 30,
):
    """Sugere horários com base no histórico do customer e disponibilidade atual."""
    from app.services import working_hours_service
    base_date = _parse_optional_start_date(start_date)
    max_date = base_date + timedelta(days=search_days)

    customer = bundle.customers.get_by_name(customer_name)
    history = bundle.schedules.list_by_customer(customer.id) if customer else []

    # Mapeia horários ativos de trabalho por dia da semana.
    working_hours_map = {
        item.weekday: item
        for item in bundle.working_hours.list_active()
    }

    suggestions: list[dict] = []
    seen_pairs: set[tuple[date_type, time]] = set()

    # Aprende preferência por recorrência: combina dia da semana + horário.
    preference_stats: dict[tuple[int, time], dict[str, int | date_type]] = defaultdict(
        lambda: {"count": 0, "latest_date": date_type.min}
    )
    for item in history:
        key = (item.date.weekday(), item.time)
        preference_stats[key]["count"] += 1
        if item.date > preference_stats[key]["latest_date"]:
            preference_stats[key]["latest_date"] = item.date

    ranked_preferences = sorted(
        preference_stats.items(),
        key=lambda entry: (
            entry[1]["count"],
            entry[1]["latest_date"],
        ),
        reverse=True,
    )

    for (preferred_weekday, preferred_time), stats in ranked_preferences:
        if len(suggestions) >= limit:
            break

        day_offset = (preferred_weekday - base_date.weekday()) % 7
        candidate_date = base_date + timedelta(days=day_offset)
        if candidate_date == base_date and preferred_time < datetime.now().time():
            candidate_date += timedelta(days=7)

        while candidate_date <= max_date:
            pair = (candidate_date, preferred_time)
            if pair not in seen_pairs:
                is_available = (
                    _is_within_working_hours(bundle.working_hours, candidate_date, preferred_time)
                    and not bundle.schedules.check_conflict(candidate_date, preferred_time)
                )
                if is_available:
                    seen_pairs.add(pair)
                    suggestions.append(
                        {
                            "date": candidate_date,
                            "time": preferred_time,
                            "score": int(stats["count"]),
                            "source": "history_preference",
                        }
                    )
                    break

            candidate_date += timedelta(days=7)

    # Fallback: completa sugestões com primeiros slots livres futuros.
    current_date = base_date
    while len(suggestions) < limit and current_date <= max_date:
        day_working_hours = working_hours_map.get(current_date.weekday())
        if day_working_hours:
            for slot in _build_daily_slots(day_working_hours):
                pair = (current_date, slot)
                if pair in seen_pairs:
                    continue

                if not bundle.schedules.check_conflict(current_date, slot):
                    seen_pairs.add(pair)
                    suggestions.append(
                        {
                            "date": current_date,
                            "time": slot,
                            "score": 0,
                            "source": "next_available",
                        }
                    )
                    if len(suggestions) >= limit:
                        break

        current_date += timedelta(days=1)

    return {"customer_name": customer_name, "suggestions": suggestions[:limit]}
