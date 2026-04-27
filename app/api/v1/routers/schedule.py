from fastapi import APIRouter, Depends

from app.core.dependencies import ScheduleBundle, get_schedule_bundle
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
def list_schedules(bundle: ScheduleBundle = Depends(get_schedule_bundle)):
    """Lista todos os agendamentos registrados"""
    return schedule_service.list_schedules(bundle)


# 🔹 OBTER AGENDAMENTO POR ID
@router.get("/{id}", response_model=ScheduleResponse)
def get_schedule(id: int, bundle: ScheduleBundle = Depends(get_schedule_bundle)):
    """Obtém um agendamento específico pelo ID"""
    return schedule_service.get_schedule(bundle, id)


# 🔹 CRIAR NOVO AGENDAMENTO
@router.post("/", response_model=ScheduleResponse, status_code=201)
def create_schedule(
    payload: ScheduleCreate,
    bundle: ScheduleBundle = Depends(get_schedule_bundle),
):
    """Cria um novo agendamento com os dados fornecidos em JSON"""
    return schedule_service.create_schedule(
        bundle,
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
    bundle: ScheduleBundle = Depends(get_schedule_bundle),
):
    """Atualiza um agendamento existente com novos dados"""
    return schedule_service.update_schedule(
        bundle,
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
    bundle: ScheduleBundle = Depends(get_schedule_bundle),
):
    """Deleta um agendamento pelo ID"""
    schedule_service.delete_schedule(bundle, id)


@router.post("/suggestions", response_model=ScheduleSuggestionResponse)
def suggest_schedule(
    payload: ScheduleSuggestionRequest,
    bundle: ScheduleBundle = Depends(get_schedule_bundle),
):
    """Sugere horários recorrentes com base no histórico e disponibilidade."""
    return schedule_service.suggest_schedules(
        bundle,
        customer_name=payload.customer_name,
        start_date=payload.start_date,
        limit=payload.limit,
        search_days=payload.search_days,
    )