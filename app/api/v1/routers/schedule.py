from fastapi import APIRouter, Depends

from app.database.session import get_db
from app.schemas import ScheduleCreate
from app.services import schedule_service


router = APIRouter(prefix="/schedule", tags=["Schedule"])


# 🔹 LISTAR TODOS OS AGENDAMENTOS
@router.get("/")
def list_schedules(db = Depends(get_db)):
    """Lista todos os agendamentos registrados"""
    return schedule_service.list_schedules(db)


# 🔹 OBTER AGENDAMENTO POR ID
@router.get("/{id}")
def get_schedule(id: int, db = Depends(get_db)):
    """Obtém um agendamento específico pelo ID"""
    return schedule_service.get_schedule(db, id)


# 🔹 CRIAR NOVO AGENDAMENTO
@router.post("/")
def create_schedule(
    payload: ScheduleCreate,
    db = Depends(get_db),
):
    """Cria um novo agendamento com os dados fornecidos em JSON
    
    Parâmetros:
    - client_name: Nome do cliente
    - date: Data no formato DD/MM/YYYY
    - time: Horário no formato HH:MM:SS
    """
    return schedule_service.create_schedule(db, payload.client_name, payload.date, payload.time)


# 🔹 ATUALIZAR AGENDAMENTO
@router.put("/{id}")
def put_schedule(
    id: int,
    payload: ScheduleCreate,
    db = Depends(get_db),
):
    """Atualiza um agendamento existente com novos dados
    
    Parâmetros:
    - id: ID do agendamento a atualizar
    - client_name: Novo nome do cliente
    - date: Nova data no formato DD/MM/YYYY
    - time: Novo horário no formato HH:MM:SS
    """
    return schedule_service.update_schedule(db, id, payload.client_name, payload.date, payload.time)


# 🔹 DELETAR AGENDAMENTO
@router.delete("/{id}")
def delete_schedule(id: int, db = Depends(get_db)):
    """Deleta um agendamento pelo ID
    
    Parâmetros:
    - id: ID do agendamento a deletar
    """
    return schedule_service.delete_schedule(db, id)