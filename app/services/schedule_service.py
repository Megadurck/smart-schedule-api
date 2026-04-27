from collections import defaultdict
from datetime import datetime, time, date as date_type, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import customer_repository, schedule_repository
from app.repositories import customer_repository, professional_repository, schedule_repository
from app.services import working_hours_service
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

def validate_working_hours(
    db: Session,
    company_id: int,
    schedule_date: date_type,
    schedule_time: time,
) -> bool:
    """Verifica se o horário está dentro do horário de funcionamento do dia.
    
    Retorna ``True`` se está dentro, ``False`` caso contrário.
    """
    weekday = schedule_date.weekday()  # 0 = segunda, 6 = domingo
    return working_hours_service.is_within_working_hours(
        db,
        company_id,
        weekday,
        schedule_time,
    )


# ---------------------------------------------------------------------------
# Operações de Negócio (usando repositories)
# ---------------------------------------------------------------------------

def list_schedules(db: Session, company_id: int):
    """Lista todos os agendamentos."""
    return schedule_repository.list_schedules(db, company_id)


def get_schedule(db: Session, schedule_id: int, company_id: int):
    """Obtém um agendamento por ID."""
    schedule = schedule_repository.get_schedule(db, schedule_id, company_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return schedule


def create_schedule(
    db: Session,
    company_id: int,
    customer_name: str,
    date_str: str,
    time_str: str,
    professional_id: int | None = None,
):
    """Cria um novo agendamento com validações de negócio."""
    # Parsing
    schedule_date, schedule_time = parse_date_time(date_str, time_str)

    # Validações de negócio
    if schedule_repository.check_conflict(db, company_id, schedule_date, schedule_time):
        raise HTTPException(status_code=409, detail="Horário já ocupado")
    
    if not validate_working_hours(db, company_id, schedule_date, schedule_time):
        raise HTTPException(
            status_code=422,
            detail="Horário fora do funcionamento. Verifique os horários de trabalho disponíveis.",
        )

    # Obter ou criar customer final
    customer = customer_repository.find_or_create_customer(db, customer_name, company_id)
    professional = _get_professional_or_none(db, company_id, professional_id)

    # Persistência (delegada ao repository)
    return schedule_repository.create_schedule(
        db,
        customer.id,
        company_id,
        professional.id if professional else None,
        schedule_date,
        schedule_time,
    )


def update_schedule(
    db: Session,
    company_id: int,
    schedule_id: int,
    customer_name: str,
    date_str: str,
    time_str: str,
    professional_id: int | None = None,
):
    """Atualiza um agendamento com validações de negócio."""
    # Parsing
    schedule_date, schedule_time = parse_date_time(date_str, time_str)

    # Validações de negócio
    if schedule_repository.check_conflict(
        db,
        company_id,
        schedule_date,
        schedule_time,
        exclude_id=schedule_id,
    ):
        raise HTTPException(status_code=409, detail="Horário já ocupado")
    
    if not validate_working_hours(db, company_id, schedule_date, schedule_time):
        raise HTTPException(
            status_code=422,
            detail="Horário fora do funcionamento. Verifique os horários de trabalho disponíveis.",
        )

    # Obter ou criar customer final
    customer = customer_repository.find_or_create_customer(db, customer_name, company_id)
    professional = _get_professional_or_none(db, company_id, professional_id)

    # Persistência (delegada ao repository)
    schedule = schedule_repository.update_schedule(
        db,
        schedule_id,
        customer.id,
        company_id,
        professional.id if professional else None,
        schedule_date,
        schedule_time,
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    return schedule


def _get_professional_or_none(db: Session, company_id: int, professional_id: int | None):
    if professional_id is None:
        return None

    professional = professional_repository.get_professional(db, professional_id, company_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional nao encontrado")
    return professional


def delete_schedule(db: Session, company_id: int, schedule_id: int):
    """Deleta um agendamento."""
    deleted = schedule_repository.delete_schedule(db, schedule_id, company_id)
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
    db: Session,
    company_id: int,
    customer_name: str,
    start_date: str | None = None,
    limit: int = 3,
    search_days: int = 30,
):
    """Sugere horários com base no histórico do customer e disponibilidade atual."""
    base_date = _parse_optional_start_date(start_date)
    max_date = base_date + timedelta(days=search_days)

    customer = customer_repository.get_customer_by_name(db, customer_name, company_id)
    history = (
        schedule_repository.list_schedules_by_customer(db, customer.id, company_id)
        if customer
        else []
    )

    # Mapeia horários ativos de trabalho por dia da semana.
    working_hours_map = {
        item.weekday: item
        for item in db.query(WorkingHours)
        .filter(WorkingHours.company_id == company_id, WorkingHours.is_active == True)
        .all()
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
                    validate_working_hours(db, company_id, candidate_date, preferred_time)
                    and not schedule_repository.check_conflict(
                        db,
                        company_id,
                        candidate_date,
                        preferred_time,
                    )
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

                if not schedule_repository.check_conflict(db, company_id, current_date, slot):
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
