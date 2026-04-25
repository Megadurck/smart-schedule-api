import re

from fastapi import HTTPException

from agent.config import AGENT_PROVIDER
from agent import tools


def parse_intent(message: str) -> dict:
    text = message.strip().lower()

    if any(word in text for word in ["horario", "horarios", "dispon", "vaga", "vagas"]):
        return {
            "action": "list_slots",
            "date": _extract_date(message),
        }

    if any(word in text for word in ["agendar", "marcar"]):
        return {
            "action": "create_schedule",
            "client_name": _extract_name(message),
            "date": _extract_date(message),
            "time": _extract_time(message),
        }

    return {"action": "help"}


def handle_message(message: str) -> str:
    intent = parse_intent(message)
    db = tools.get_db_session()
    try:
        if intent["action"] == "list_slots":
            slots = tools.list_available_slots(
                db,
                start_date=intent.get("date"),
                days_ahead=7,
                limit=8,
            )
            if not slots:
                return "Nao encontrei horarios disponiveis no periodo informado."

            human_slots = ", ".join(
                f"{item['date'].strftime('%d/%m/%Y')} {item['time'].strftime('%H:%M:%S')}"
                for item in slots
            )
            return f"Horarios disponiveis: {human_slots}"

        if intent["action"] == "create_schedule":
            client_name = intent.get("client_name")
            schedule_date = intent.get("date")
            schedule_time = intent.get("time")

            if not client_name or not schedule_date or not schedule_time:
                return (
                    "Para agendar, use: agendar nome Maria em 03/03/2026 09:00:00"
                )

            created = tools.create_schedule_offline(
                db,
                client_name=client_name,
                schedule_date=schedule_date,
                schedule_time=schedule_time,
            )
            return (
                f"Agendamento confirmado para {created.client.name} em "
                f"{created.date.strftime('%d/%m/%Y')} as {created.time.strftime('%H:%M:%S')}."
            )

        return (
            "Posso listar horarios e agendar. Exemplos: "
            "'horarios para 03/03/2026' ou 'agendar nome Maria em 03/03/2026 09:00:00'."
        )
    except HTTPException as exc:
        return f"Erro: {exc.detail}"
    except ValueError:
        return "Erro de formato. Use data DD/MM/YYYY e hora HH:MM ou HH:MM:SS."
    finally:
        db.close()


def _extract_date(message: str) -> str | None:
    match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", message)
    return match.group(1) if match else None


def _extract_time(message: str) -> str | None:
    match = re.search(r"\b(\d{2}:\d{2}(?::\d{2})?)\b", message)
    if not match:
        return None

    value = match.group(1)
    if len(value) == 5:
        return f"{value}:00"
    return value


def _extract_name(message: str) -> str | None:
    patterns = [
        r"nome\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s'-]{1,40})",
        r"para\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s'-]{1,40})",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def run_cli() -> None:
    print(f"Agent provider: {AGENT_PROVIDER}")
    print("Digite uma mensagem (ou 'sair' para encerrar)")
    while True:
        raw = input("> ").strip()
        if raw.lower() in {"sair", "exit", "quit"}:
            print("Encerrado.")
            break

        print(handle_message(raw))


if __name__ == "__main__":
    run_cli()