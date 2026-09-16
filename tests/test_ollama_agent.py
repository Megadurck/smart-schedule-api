"""
Test script for Ollama agent integration
"""
import logging
import sys
from datetime import date, datetime, time
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure project root is importable when running this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agent.agent import handle_message, parse_intent_simple


def test_parse_intent_simple_cancel_schedule():
    intent = parse_intent_simple("Cancelar Maria Silva em 12/08/2026 às 09:30")
    assert intent["action"] == "delete_schedule"
    assert intent["customer_name"] == "Maria Silva"
    assert intent["date"] == "12/08/2026"
    assert intent["time"] == "09:30:00"


def test_handle_message_delete_schedule():
    schedule = {
        "id": 42,
        "customer_name": "Maria Silva",
        "date": date(2026, 8, 12),
        "time": time(9, 30),
        "status": "pending",
    }

    with patch("agent.agent.tools.list_schedules", return_value=[schedule]), patch(
        "agent.agent.tools.delete_schedule"
    ) as delete_schedule:
        response = handle_message("Cancelar Maria Silva em 12/08/2026 às 09:30")

    assert "cancelado" in response.lower()
    delete_schedule.assert_called_once_with(42)


def test_handle_message_out_of_business_hours_is_natural():
    with patch(
        "agent.agent.tools.create_schedule",
        side_effect=HTTPException(
            status_code=422,
            detail="Horário fora do funcionamento. Verifique os horários de trabalho disponíveis.",
        ),
    ):
        response = handle_message("Quero agendar Maria Silva em 12/08/2026 às 07:00")

    assert "fora do horário de funcionamento" in response.lower()
    assert "escolha outro horário" in response.lower()


def test_schedule_api_client_uses_agent_company_name_from_env(monkeypatch):
    monkeypatch.setenv("AGENT_COMPANY_NAME", "Clínica de Olhos da LU")

    import importlib
    import agent.config
    import agent.api_client

    importlib.reload(agent.config)
    importlib.reload(agent.api_client)

    client = agent.api_client.ScheduleApiClient()
    assert client.company_name == "Clínica de Olhos da LU"


def test_handle_message_list_slots_grouped_by_date():
    slots = [
        {"date": date(2026, 8, 12), "time": time(8, 0)},
        {"date": date(2026, 8, 12), "time": time(8, 30)},
        {"date": date(2026, 8, 12), "time": time(9, 0)},
        {"date": date(2026, 8, 12), "time": time(17, 30)},
    ]

    with patch("agent.agent.tools.list_available_slots", return_value=slots) as list_available_slots:
        response = handle_message("Quais são os horários para 12/08/2026?")

    assert list_available_slots.call_args.kwargs["start_date"] == "12/08/2026"
    assert list_available_slots.call_args.kwargs["days_ahead"] == 1
    assert "12/08/2026" in response
    assert "Horário de funcionamento" in response
    assert "08:00" in response
    assert "17:30" in response
    assert "Slots disponíveis" in response


def test_send_whatsapp_message_uses_neonize_when_configured(monkeypatch):
    captured = {}

    class FakeClient:
        connected = False
        is_connected = True

        def send_message(self, to, message, link_preview=False, ghost_mentions=None, mentions_are_lids=False, add_msg_secret=False):
            captured["to"] = to
            captured["message"] = message
            captured["link_preview"] = link_preview
            return {"status": "ok"}

    def fake_connect(self):
        captured["connect_called"] = True
        self.connected = True

    monkeypatch.setenv("WHATSAPP_PROVIDER", "neonize")
    monkeypatch.setattr("agent.whatsapp_client.get_neonize_client", lambda: FakeClient())
    monkeypatch.setattr("agent.whatsapp_client._normalize_whatsapp_target", lambda value: "5511999998888")
    monkeypatch.setattr("agent.whatsapp_client._is_neonize_connected", lambda client: True)

    from agent import whatsapp_client

    whatsapp_client.send_whatsapp_message("+5511999998888", "Olá do Smart Schedule")

    assert getattr(captured["to"], "User", None) == "5511999998888"
    assert captured["message"] == "Olá do Smart Schedule"
    assert captured["link_preview"] is False
    assert "connect_called" not in captured


def test_neonize_connected_state_uses_property_not_method(monkeypatch):
    class FakeClient:
        connected = False
        is_connected = True

    from agent import whatsapp_client

    assert whatsapp_client._is_neonize_connected(FakeClient()) is True


def test_get_neonize_client_registers_message_event(monkeypatch):
    monkeypatch.setenv("WHATSAPP_PROVIDER", "neonize")
    monkeypatch.setattr("agent.whatsapp_client._NEONIZE_CLIENT", None)

    from agent import whatsapp_client

    client = whatsapp_client.get_neonize_client()

    assert client is not None
    assert client.event.list_func


def test_render_qr_from_neonize_url_bytes(monkeypatch):
    from io import StringIO

    from agent import whatsapp_client

    stream = StringIO()
    with patch("sys.stdout", stream):
        rendered = whatsapp_client._render_qr_to_terminal(b"https://wa.me/settings/linked_devices#abc")

    assert rendered == "qr-rendered"
    assert "https://wa.me/settings/linked_devices#abc" not in stream.getvalue()
    assert any(symbol in stream.getvalue() for symbol in ("█", "##", "██", "  "))


# Test cases
test_messages = [
    "Quais são os horários disponíveis para 03/03/2026?",
    "Quero agendar Maria Silva em 05/03/2026 às 14:00",
    "Pode me mostrar os horários?",
    "Agendar João em 10/03/2026 10:30",
    "Oi, como funciona?",
]

if __name__ == "__main__":
    print("=" * 60)
    print("Testando Agent com Ollama")
    print("=" * 60)

    for msg in test_messages:
        print(f"\n👤 Usuário: {msg}")
        try:
            response = handle_message(msg)
            print(f"🤖 Agent: {response}")
        except Exception as e:
            print(f"❌ Erro: {e}")
            logger.exception("Erro ao processar mensagem")

    print("\n" + "=" * 60)
