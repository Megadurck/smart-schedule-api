from sqlalchemy.orm import Session, joinedload

from app.models.schedule_model import Schedule


def list_schedules(db: Session) -> list[Schedule]:
    """Lista todos os agendamentos com cliente carregado."""
    return db.query(Schedule).options(joinedload(Schedule.client)).all()


def get_schedule(db: Session, schedule_id: int) -> Schedule | None:
    """Obtém um agendamento por ID."""
    return (
        db.query(Schedule)
        .options(joinedload(Schedule.client))
        .filter(Schedule.id == schedule_id)
        .first()
    )


def create_schedule(db: Session, client_id: int, schedule_date, schedule_time) -> Schedule:
    """Cria um novo agendamento."""
    new_schedule = Schedule(
        client_id=client_id, date=schedule_date, time=schedule_time
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    # Reload with relationship
    return (
        db.query(Schedule)
        .options(joinedload(Schedule.client))
        .filter(Schedule.id == new_schedule.id)
        .first()
    )


def update_schedule(
    db: Session, schedule_id: int, client_id: int, schedule_date, schedule_time
) -> Schedule:
    """Atualiza um agendamento existente."""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        return None

    schedule.client_id = client_id
    schedule.date = schedule_date
    schedule.time = schedule_time

    db.commit()
    db.refresh(schedule)

    return (
        db.query(Schedule)
        .options(joinedload(Schedule.client))
        .filter(Schedule.id == schedule.id)
        .first()
    )


def delete_schedule(db: Session, schedule_id: int) -> bool:
    """Deleta um agendamento."""
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not schedule:
        return False

    db.delete(schedule)
    db.commit()
    return True


def check_conflict(
    db: Session, schedule_date, schedule_time, exclude_id: int | None = None
) -> bool:
    """Verifica se já existe outro agendamento no mesmo horário."""
    query = db.query(Schedule).filter(
        Schedule.date == schedule_date, Schedule.time == schedule_time
    )
    if exclude_id is not None:
        query = query.filter(Schedule.id != exclude_id)

    return db.query(query.exists()).scalar()
