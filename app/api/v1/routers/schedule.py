from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_client
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
def list_schedules(db = Depends(get_db)):
    """Lista todos os agendamentos registrados"""
    return schedule_service.list_schedules(db)


# 🔹 OBTER AGENDAMENTO POR ID
@router.get("/{id}", response_model=ScheduleResponse)
def get_schedule(id: int, db = Depends(get_db)):
    """Obtém um agendamento específico pelo ID"""
    return schedule_service.get_schedule(db, id)


# 🔹 CRIAR NOVO AGENDAMENTO
@router.post("/", response_model=ScheduleResponse, status_code=201)
def create_schedule(
    payload: ScheduleCreate,
    db = Depends(get_db),
    _current_client = Depends(get_current_client),
):
    """Cria um novo agendamento com os dados fornecidos em JSON"""
    return schedule_service.create_schedule(db, payload.client_name, payload.date, payload.time)


# 🔹 ATUALIZAR AGENDAMENTO
@router.put("/{id}", response_model=ScheduleResponse)
def put_schedule(
    id: int,
    payload: ScheduleCreate,
    db = Depends(get_db),
    _current_client = Depends(get_current_client),
):
    """Atualiza um agendamento existente com novos dados"""
    return schedule_service.update_schedule(db, id, payload.client_name, payload.date, payload.time)


# 🔹 DELETAR AGENDAMENTO
@router.delete("/{id}", status_code=204)
def delete_schedule(
    id: int,
    db = Depends(get_db),
    _current_client = Depends(get_current_client),
):
    """Deleta um agendamento pelo ID"""
    schedule_service.delete_schedule(db, id)


@router.post("/suggestions", response_model=ScheduleSuggestionResponse)
def suggest_schedule(
    payload: ScheduleSuggestionRequest,
    db = Depends(get_db),
    _current_client = Depends(get_current_client),
):
    """Sugere horários recorrentes com base no histórico e disponibilidade."""
    return schedule_service.suggest_schedules(
        db,
        client_name=payload.client_name,
        start_date=payload.start_date,
        limit=payload.limit,
        search_days=payload.search_days,
    )