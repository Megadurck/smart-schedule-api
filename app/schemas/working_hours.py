"""Schemas de horário de funcionamento.

Este módulo centraliza os contratos de entrada e saída da API de expediente.
"""

from datetime import time
from typing import Union

from pydantic import BaseModel, field_validator

from app.enum.weekday import Weekday


class WorkingHoursCreate(BaseModel):
    """Payload para criar/atualizar horário de funcionamento."""

    # Aceita número (0-6) ou nome do enum (ex.: MONDAY).
    weekday: Weekday
    # Mantido como string para preservar a resposta/erros atuais da API.
    start_time: str
    end_time: str
    slot_duration_minutes: int = 30
    lunch_start: str | None = "12:00:00"
    lunch_end: str | None = "14:00:00"

    @field_validator("weekday", mode="before")
    @classmethod
    def validate_weekday(cls, value: Union[str, int]) -> Weekday:
        """Converte weekday para enum e padroniza mensagens de erro."""
        if isinstance(value, str):
            try:
                return Weekday[value.upper()]
            except KeyError as exc:
                raise ValueError(f"Invalid weekday name: {value}") from exc

        if isinstance(value, int):
            try:
                return Weekday(value)
            except ValueError as exc:
                raise ValueError(f"Invalid weekday value: {value}") from exc

        raise ValueError("Weekday must be int or str")


# ---------------------------------------------------------------------------
# Schemas de saída (o que a API devolve)
# ---------------------------------------------------------------------------

class WorkingHoursResponse(BaseModel):
    """Resposta de um horário de funcionamento: expõe só campos seguros."""

    id: int
    weekday: int
    # Pydantic serializa datetime.time para string "HH:MM:SS" automaticamente.
    start_time: time
    end_time: time
    slot_duration_minutes: int
    lunch_start: time | None
    lunch_end: time | None
    is_active: bool

    model_config = {"from_attributes": True}
