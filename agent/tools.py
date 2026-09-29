"""
Bridge between the agent's message handling and the Smart Schedule API.

O agent nao acessa mais o banco/serviços diretamente: todas as operações
passam pelo ScheduleApiClient (HTTP), do mesmo jeito que o frontend consome
a API.
"""
from agent.api_client import ScheduleApiClient

_client: ScheduleApiClient | None = None


def get_api_client() -> ScheduleApiClient:
	"""Retorna um client HTTP compartilhado, criando na primeira chamada."""
	global _client
	if _client is None:
		_client = ScheduleApiClient()
	return _client


def list_available_slots(
	start_date: str | None,
	days_ahead: int = 7,
	limit: int = 200,
) -> list[dict]:
	return get_api_client().list_available_slots(start_date, days_ahead=days_ahead, limit=limit)


def list_my_schedules(whatsapp_phone: str) -> list[dict]:
	return get_api_client().list_my_schedules(whatsapp_phone)


def create_schedule(
	customer_name: str,
	schedule_date: str,
	schedule_time: str,
	whatsapp_phone: str,
) -> dict:
	return get_api_client().create_schedule(
		customer_name,
		schedule_date,
		schedule_time,
		whatsapp_phone,
	)


def cancel_my_schedule(schedule_id: int, whatsapp_phone: str) -> None:
	return get_api_client().cancel_my_schedule(schedule_id, whatsapp_phone)
