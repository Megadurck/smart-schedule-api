from datetime import datetime, time, date as date_type

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import schedule_repository, client_repository
from app.services import working_hours_service


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
    db: Session, schedule_date: date_type, schedule_time: time
) -> bool:
    """Verifica se o horário está dentro do horário de funcionamento do dia.
    
    Retorna ``True`` se está dentro, ``False`` caso contrário.
    """
    weekday = schedule_date.weekday()  # 0 = segunda, 6 = domingo
    return working_hours_service.is_within_working_hours(db, weekday, schedule_time)


# ---------------------------------------------------------------------------
# Operações de Negócio (usando repositories)
# ---------------------------------------------------------------------------

def list_schedules(db: Session):
    """Lista todos os agendamentos."""
    return schedule_repository.list_schedules(db)


def get_schedule(db: Session, schedule_id: int):
    """Obtém um agendamento por ID."""
    schedule = schedule_repository.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return schedule


def create_schedule(db: Session, client_name: str, date_str: str, time_str: str):
    """Cria um novo agendamento com validações de negócio."""
    # Parsing
    schedule_date, schedule_time = parse_date_time(date_str, time_str)

    # Validações de negócio
    if schedule_repository.check_conflict(db, schedule_date, schedule_time):
        raise HTTPException(status_code=409, detail="Horário já ocupado")
    
    if not validate_working_hours(db, schedule_date, schedule_time):
        raise HTTPException(
            status_code=422,
            detail="Horário fora do funcionamento. Verifique os horários de trabalho disponíveis.",
        )

    # Obter ou criar cliente
    client = client_repository.find_or_create_client(db, client_name)

    # Persistência (delegada ao repository)
    return schedule_repository.create_schedule(db, client.id, schedule_date, schedule_time)


def update_schedule(
    db: Session, schedule_id: int, client_name: str, date_str: str, time_str: str
):
    """Atualiza um agendamento com validações de negócio."""
    # Parsing
    schedule_date, schedule_time = parse_date_time(date_str, time_str)

    # Validações de negócio
    if schedule_repository.check_conflict(db, schedule_date, schedule_time, exclude_id=schedule_id):
        raise HTTPException(status_code=409, detail="Horário já ocupado")
    
    if not validate_working_hours(db, schedule_date, schedule_time):
        raise HTTPException(
            status_code=422,
            detail="Horário fora do funcionamento. Verifique os horários de trabalho disponíveis.",
        )

    # Obter ou criar cliente
    client = client_repository.find_or_create_client(db, client_name)

    # Persistência (delegada ao repository)
    schedule = schedule_repository.update_schedule(db, schedule_id, client.id, schedule_date, schedule_time)
    if not schedule:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    
    return schedule


def delete_schedule(db: Session, schedule_id: int):
    """Deleta um agendamento."""
    deleted = schedule_repository.delete_schedule(db, schedule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return {"detail": "Agendamento deletado"}
