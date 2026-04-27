from fastapi import APIRouter, Depends, HTTPException
from datetime import time as time_type

from app.core.dependencies import get_working_hours_repo
from app.repositories.working_hours_repository import WorkingHoursRepository
from app.services import working_hours_service
from app.enum.weekday import Weekday
from app.schemas import WorkingHoursCreate, WorkingHoursResponse


router = APIRouter(prefix="/working-hours", tags=["Working Hours"])


# 🔹 LISTAR TODOS OS HORÁRIOS DE FUNCIONAMENTO
@router.get("/", response_model=list[WorkingHoursResponse])
def list_working_hours(repo: WorkingHoursRepository = Depends(get_working_hours_repo)):
    """Lista todos os horários de funcionamento configurados"""
    return working_hours_service.list_working_hours(repo)


# 🔹 DEFINIR HORÁRIO DE FUNCIONAMENTO
@router.post("/", response_model=WorkingHoursResponse, status_code=201)
def set_working_hours(
    payload: WorkingHoursCreate,
    repo: WorkingHoursRepository = Depends(get_working_hours_repo),
):
    """Define o horário de funcionamento para um dia da semana via JSON
    
    Parâmetros:
    - weekday: Dia da semana (0=segunda, 1=terça, 2=quarta, 3=quinta, 4=sexta, 5=sábado, 6=domingo)
    - start_time: Horário de início no formato HH:MM:SS
    - end_time: Horário de fim no formato HH:MM:SS
    - slot_duration_minutes: Duração de cada slot em minutos (padrão 30)
    - lunch_start: Horário de início do almoço (padrão 12:00:00)
    - lunch_end: Horário de fim do almoço (padrão 14:00:00)
    """
    return _validate_and_set_working_hours(
        repo,
        payload.weekday,
        payload.start_time,
        payload.end_time,
        payload.slot_duration_minutes,
        payload.lunch_start,
        payload.lunch_end,
    )


# 🔹 CALCULAR SLOTS DISPONÍVEIS
@router.get("/slots/{weekday}")
def get_available_slots(
    weekday: Weekday,
    repo: WorkingHoursRepository = Depends(get_working_hours_repo),
):
    """Calcula quantos slots de atendimento estão disponíveis para um dia
    
    Exemplo de resposta:
    {
        "weekday": 0,
        "available_slots": 16,
        "total_available_minutes": 480,
        "lunch_duration_minutes": 120,
        "slot_duration_minutes": 30
    }
    """
    return working_hours_service.calculate_available_slots(repo, weekday.value)


def _validate_and_set_working_hours(
    repo: WorkingHoursRepository,
    weekday: Weekday,
    start_time: str,
    end_time: str,
    slot_duration_minutes: int = 30,
    lunch_start: str | None = "12:00:00",
    lunch_end: str | None = "14:00:00"
):
    """Realiza validações de domínio e configura horários de funcionamento
    
    Validações aplicadas:
    - Formatos de hora devem ser HH:MM:SS
    - Hora inicial deve ser anterior à hora final
    - Se almoço definido: início deve ser anterior ao fim
    - Almoço deve estar completamente dentro do horário de trabalho
    - Duração de slot deve ser positiva
    - Weekday deve estar entre 0 e 6
    
    Retorna:
    - Objeto WorkingHours criado ou atualizado
    """
    try:
        start = time_type.fromisoformat(start_time)
        end = time_type.fromisoformat(end_time)
        lunch_start_time = time_type.fromisoformat(lunch_start) if lunch_start else None
        lunch_end_time = time_type.fromisoformat(lunch_end) if lunch_end else None
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de hora inválido. Use HH:MM:SS",
        )

    if start >= end:
        raise HTTPException(
            status_code=400,
            detail="A hora inicial deve ser anterior à hora final",
        )

    if lunch_start_time and lunch_end_time:
        if lunch_start_time >= lunch_end_time:
            raise HTTPException(
                status_code=400,
                detail="A hora de início do almoço deve ser anterior à de fim",
            )
        if not (start <= lunch_start_time and lunch_end_time <= end):
            raise HTTPException(
                status_code=400,
                detail="Horário de almoço deve estar dentro do expediente",
            )

    if slot_duration_minutes <= 0:
        raise HTTPException(
            status_code=400,
            detail="Duração do slot deve ser maior que 0 minutos",
        )

    if weekday.value < 0 or weekday.value > 6:
        raise HTTPException(
            status_code=400,
            detail="weekday deve estar entre 0 (segunda) e 6 (domingo)",
        )

    return working_hours_service.set_working_hours(
        repo,
        weekday.value,
        start,
        end,
        slot_duration_minutes,
        lunch_start_time,
        lunch_end_time,
    )
