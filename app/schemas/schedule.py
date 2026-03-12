"""Schemas de agendamento.

Este módulo concentra os contratos de entrada da API de agendamentos.
"""

from pydantic import BaseModel


class ScheduleCreate(BaseModel):
    """Payload de criação/atualização de agendamento."""

    # Nome do cliente usado para localizar ou criar o cadastro.
    client_name: str
    # Data no formato DD/MM/YYYY (regra de parse fica no service).
    date: str
    # Hora no formato HH:MM:SS (regra de parse fica no service).
    time: str
