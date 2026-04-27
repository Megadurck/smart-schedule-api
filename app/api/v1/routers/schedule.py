from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.schemas import (
    ScheduleCreate,
    ScheduleResponse,
    ScheduleSuggestionRequest,
    ScheduleSuggestionResponse,
)
from app.services import schedule_service


router = APIRouter(prefix="/schedule", tags=["Schedule"])


# 🔹 LISTAR TODOS OS AGENDAMENTOS
@router.get("/", response_model=list[ScheduleResponse])
def list_schedules(
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Lista todos os agendamentos registrados"""
    return schedule_service.list_schedules(db, current_user.company_id)


# 🔹 OBTER AGENDAMENTO POR ID
@router.get("/{id}", response_model=ScheduleResponse)
def get_schedule(
    id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Obtém um agendamento específico pelo ID"""
    return schedule_service.get_schedule(db, id, current_user.company_id)


# 🔹 CRIAR NOVO AGENDAMENTO
@router.post("/", response_model=ScheduleResponse, status_code=201)
def create_schedule(
    payload: ScheduleCreate,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Cria um novo agendamento com os dados fornecidos em JSON"""
    return schedule_service.create_schedule(
        db,
        current_user.company_id,
        payload.customer_name,
        payload.date,
        payload.time,
        payload.professional_id,
    )


# 🔹 ATUALIZAR AGENDAMENTO
@router.put("/{id}", response_model=ScheduleResponse)
def put_schedule(
    id: int,
    payload: ScheduleCreate,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Atualiza um agendamento existente com novos dados"""
    return schedule_service.update_schedule(
        db,
        current_user.company_id,
        id,
        payload.customer_name,
        payload.date,
        payload.time,
        payload.professional_id,
    )


# 🔹 DELETAR AGENDAMENTO
@router.delete("/{id}", status_code=204)
def delete_schedule(
    id: int,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Deleta um agendamento pelo ID"""
    schedule_service.delete_schedule(db, current_user.company_id, id)


@router.post("/suggestions", response_model=ScheduleSuggestionResponse)
def suggest_schedule(
    payload: ScheduleSuggestionRequest,
    db = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Sugere horários recorrentes com base no histórico e disponibilidade."""
    return schedule_service.suggest_schedules(
        db,
        company_id=current_user.company_id,
        customer_name=payload.customer_name,
        start_date=payload.start_date,
        limit=payload.limit,
        search_days=payload.search_days,
    )