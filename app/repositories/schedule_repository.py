from sqlalchemy.orm import Session, joinedload

from app.models.schedule_model import Schedule


def list_schedules(db: Session, company_id: int) -> list[Schedule]:
    """Lista todos os agendamentos com customer carregado."""
    return (
        db.query(Schedule)
        .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
        .filter(Schedule.company_id == company_id)
        .all()
    )


def get_schedule(db: Session, schedule_id: int, company_id: int) -> Schedule | None:
    """Obtém um agendamento por ID."""
    return (
        db.query(Schedule)
        .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
        .filter(Schedule.id == schedule_id, Schedule.company_id == company_id)
        .first()
    )


def create_schedule(
    db: Session,
    customer_id: int,
    company_id: int,
    professional_id: int | None,
    schedule_date,
    schedule_time,
) -> Schedule:
    """Cria um novo agendamento."""
    new_schedule = Schedule(
        customer_id=customer_id,
        company_id=company_id,
        professional_id=professional_id,
        date=schedule_date,
        time=schedule_time,
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    # Reload with relationship — sempre filtra por company_id para garantir isolamento
    return (
        db.query(Schedule)
        .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
        .filter(Schedule.id == new_schedule.id, Schedule.company_id == company_id)
        .first()
    )


def update_schedule(
    db: Session,
    schedule_id: int,
    customer_id: int,
    company_id: int,
    professional_id: int | None,
    schedule_date,
    schedule_time,
) -> Schedule:
    """Atualiza um agendamento existente."""
    schedule = (
        db.query(Schedule)
        .filter(Schedule.id == schedule_id, Schedule.company_id == company_id)
        .first()
    )
    if not schedule:
        return None

    schedule.customer_id = customer_id
    schedule.company_id = company_id
    schedule.professional_id = professional_id
    schedule.date = schedule_date
    schedule.time = schedule_time

    db.commit()
    db.refresh(schedule)

    return (
        db.query(Schedule)
        .options(joinedload(Schedule.customer), joinedload(Schedule.professional))
        .filter(Schedule.id == schedule.id, Schedule.company_id == company_id)
        .first()
    )


def delete_schedule(db: Session, schedule_id: int, company_id: int) -> bool:
    """Deleta um agendamento."""
    schedule = (
        db.query(Schedule)
        .filter(Schedule.id == schedule_id, Schedule.company_id == company_id)
        .first()
    )
    if not schedule:
        return False

    db.delete(schedule)
    db.commit()
    return True


def check_conflict(
    db: Session,
    company_id: int,
    schedule_date,
    schedule_time,
    exclude_id: int | None = None,
) -> bool:
    """Verifica se já existe outro agendamento no mesmo horário."""
    query = db.query(Schedule).filter(
        Schedule.company_id == company_id,
        Schedule.date == schedule_date,
        Schedule.time == schedule_time,
    )
    if exclude_id is not None:
        query = query.filter(Schedule.id != exclude_id)

    return db.query(query.exists()).scalar()


def list_schedules_by_customer(db: Session, customer_id: int, company_id: int) -> list[Schedule]:
    """Lista agendamentos de um customer, do mais recente para o mais antigo."""
    return (
        db.query(Schedule)
        .filter(Schedule.customer_id == customer_id, Schedule.company_id == company_id)
        .order_by(Schedule.date.desc())
        .all()
    )
