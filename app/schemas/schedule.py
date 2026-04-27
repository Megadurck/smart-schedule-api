"""Schemas de agendamento.

Este módulo concentra os contratos de entrada e saída da API de agendamentos.
"""

from datetime import date, time

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Schemas de entrada (o que a API recebe)
# ---------------------------------------------------------------------------

class ScheduleCreate(BaseModel):
    """Payload de criação/atualização de agendamento."""

    # Nome do cliente final usado para localizar ou criar o cadastro.
    customer_name: str
    # Data no formato DD/MM/YYYY (regra de parse fica no service).
    date: str
    # Hora no formato HH:MM:SS (regra de parse fica no service).
    time: str
    professional_id: int | None = None


# ---------------------------------------------------------------------------
# Schemas de saída (o que a API devolve)
# ---------------------------------------------------------------------------

class CustomerResponse(BaseModel):
    """Dados do cliente final expostos na resposta — apenas o necessário."""

    id: int
    name: str

    # Permite que o Pydantic leia atributos de objetos SQLAlchemy diretamente.
    model_config = {"from_attributes": True}


class ProfessionalSummaryResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = {"from_attributes": True}


class ScheduleResponse(BaseModel):
    """Resposta de um agendamento: expõe só campos seguros."""

    id: int
    # Pydantic serializa datetime.date para "YYYY-MM-DD" automaticamente.
    date: date
    # Pydantic serializa datetime.time para "HH:MM:SS" automaticamente.
    time: time
    # Dados do cliente final aninhados — sem expor customer_id interno.
    customer: CustomerResponse
    professional: ProfessionalSummaryResponse | None = None

    model_config = {"from_attributes": True}


class ScheduleSuggestionRequest(BaseModel):
    """Payload para sugerir horários com base no histórico do cliente final."""

    customer_name: str
    # Data base para iniciar busca de sugestões, no formato DD/MM/YYYY.
    start_date: str | None = None
    # Quantidade máxima de sugestões retornadas.
    limit: int = Field(default=3, ge=1, le=10)
    # Janela máxima de busca de datas futuras.
    search_days: int = Field(default=30, ge=7, le=120)


class ScheduleSuggestionItem(BaseModel):
    """Representa uma sugestão de data/hora para o cliente."""

    date: date
    time: time
    score: int
    source: str


class ScheduleSuggestionResponse(BaseModel):
    """Resposta com sugestões de horário para um cliente final."""

    customer_name: str
    suggestions: list[ScheduleSuggestionItem]
