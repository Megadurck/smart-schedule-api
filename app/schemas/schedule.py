"""Schemas de agendamento.

Este módulo concentra os contratos de entrada e saída da API de agendamentos.
"""

from datetime import date, time

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Schemas de entrada (o que a API recebe)
# ---------------------------------------------------------------------------

class ScheduleCreate(BaseModel):
    """Payload de criação/atualização de agendamento."""

    # Nome do cliente usado para localizar ou criar o cadastro.
    client_name: str
    # Data no formato DD/MM/YYYY (regra de parse fica no service).
    date: str
    # Hora no formato HH:MM:SS (regra de parse fica no service).
    time: str


# ---------------------------------------------------------------------------
# Schemas de saída (o que a API devolve)
# ---------------------------------------------------------------------------

class ClientResponse(BaseModel):
    """Dados do cliente expostos na resposta — apenas o necessário."""

    id: int
    name: str

    # Permite que o Pydantic leia atributos de objetos SQLAlchemy diretamente.
    model_config = {"from_attributes": True}


class ScheduleResponse(BaseModel):
    """Resposta de um agendamento: expõe só campos seguros."""

    id: int
    # Pydantic serializa datetime.date para "YYYY-MM-DD" automaticamente.
    date: date
    # Pydantic serializa datetime.time para "HH:MM:SS" automaticamente.
    time: time
    # Dados do cliente aninhados — sem expor client_id interno.
    client: ClientResponse

    model_config = {"from_attributes": True}
