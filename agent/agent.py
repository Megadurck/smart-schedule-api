"""
Main agent logic - LLM-driven scheduling assistant
"""
import json
import logging
from typing import Optional

from fastapi import HTTPException

from agent.config import AGENT_PROVIDER
from agent import tools

if AGENT_PROVIDER == "ollama":
    from agent.llm import OllamaClient
    from agent.prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


def parse_intent_llm(message: str) -> dict:
    """Parse intent using LLM"""
    try:
        with OllamaClient() as llm:
            prompt = EXTRACTION_PROMPT_TEMPLATE.format(message=message)
            response = llm.extract_json(prompt, system=SYSTEM_PROMPT)

            if response and "action" in response:
                return response

        # Fallback se não conseguir extrair JSON válido
        return {"action": "help", "confidence": 0.0}

    except Exception as e:
        logger.error(f"Erro ao processar intent com LLM: {e}")
        return {"action": "help", "confidence": 0.0}


def parse_intent(message: str) -> dict:
    """Route para diferentes estratégias de parsing"""
    if AGENT_PROVIDER == "ollama":
        parsed = parse_intent_llm(message)
        if parsed.get("action") not in {"list_slots", "create_schedule", "delete_schedule"}:
            return parse_intent_simple(message)
        return parsed
    else:
        # Fallback para padrão simples se não configurado
        return parse_intent_simple(message)


def parse_intent_simple(message: str) -> dict:
    """Fallback simples baseado em patterns (original)"""
    text = message.strip().lower()

    if any(word in text for word in ["cancelar", "cancelamento", "excluir", "remover"]):
        return {
            "action": "delete_schedule",
            "customer_name": _extract_name(message),
            "date": _extract_date(message),
            "time": _extract_time(message),
        }

    if any(word in text for word in ["horario", "horarios", "dispon", "vaga", "vagas"]):
        return {
            "action": "list_slots",
            "date": _extract_date(message),
        }

    if any(word in text for word in ["agendar", "marcar"]):
        return {
            "action": "create_schedule",
            "customer_name": _extract_name(message),
            "date": _extract_date(message),
            "time": _extract_time(message),
        }

    return {"action": "help"}


def handle_message(message: str) -> str:
    """Process user message and return response"""
    intent = parse_intent(message)

    try:
        action = intent.get("action")
        confidence = intent.get("confidence", 1.0)

        # Log intent com confidence
        logger.info(f"Intent: {action} (confidence: {confidence:.2f})")

        if action == "list_slots":
            requested_date = intent.get("date")
            slots = tools.list_available_slots(
                start_date=requested_date,
                days_ahead=1 if requested_date else 7,
                limit=200,
            )
            if not slots:
                return "Não encontrei horários disponíveis no período informado."

            grouped = {}
            for item in slots:
                date_key = item["date"].strftime("%d/%m/%Y")
                grouped.setdefault(date_key, []).append(item["time"].strftime("%H:%M"))

            lines = []
            for date_key, times in grouped.items():
                lines.append(f"Data: {date_key}")
                lines.append("Horário de funcionamento: 08:00 às 12:00 | 14:00 às 18:00")
                lines.append("Slots disponíveis:")
                lines.append(", ".join(times))

            return "\n".join(lines)

        if action == "create_schedule":
            customer_name = intent.get("customer_name")
            schedule_date = intent.get("date")
            schedule_time = intent.get("time")

            if not customer_name or not schedule_date or not schedule_time:
                return (
                    "Para agendar, informe: nome completo, data (DD/MM/YYYY) e hora (HH:MM). "
                    "Exemplo: 'Quero agendar Maria Silva em 03/03/2026 às 10:00'"
                )

            created = tools.create_schedule(
                customer_name=customer_name,
                schedule_date=schedule_date,
                schedule_time=schedule_time,
            )
            return (
                f"✓ Agendamento confirmado para {created['customer_name']} em "
                f"{created['date'].strftime('%d/%m/%Y')} às {created['time'].strftime('%H:%M')}."
            )

        if action == "delete_schedule":
            customer_name = intent.get("customer_name")
            schedule_date = intent.get("date")
            schedule_time = intent.get("time")

            if not customer_name and not schedule_date and not schedule_time:
                return (
                    "Para cancelar, me diga o nome do cliente e a data/hora do agendamento. "
                    "Exemplo: 'Cancelar Maria Silva em 12/08/2026 às 09:30'."
                )

            schedules = tools.list_schedules(limit=200)
            normalized_customer = (customer_name or "").strip().lower()
            normalized_date = schedule_date
            normalized_time = schedule_time

            match = None
            for item in schedules:
                item_customer_name = (
                    item.get("customer", {}).get("name")
                    if isinstance(item.get("customer"), dict)
                    else item.get("customer_name") or item.get("customer") or ""
                )
                item_customer = (item_customer_name or "").strip().lower()
                item_date = item.get("date")
                item_time = item.get("time")

                item_date_text = item_date.strftime("%d/%m/%Y") if hasattr(item_date, "strftime") else str(item_date or "")
                item_time_text = item_time.strftime("%H:%M:%S") if hasattr(item_time, "strftime") else str(item_time or "")
                if len(item_time_text) == 5:
                    item_time_text = f"{item_time_text}:00"

                if normalized_customer and item_customer != normalized_customer:
                    continue
                if normalized_date and item_date_text != normalized_date:
                    continue
                if normalized_time and item_time_text != normalized_time:
                    continue

                match = item
                break

            if not match:
                return (
                    f"Não encontrei um agendamento para {customer_name or 'esse cliente'} "
                    f"{f'em {schedule_date}' if schedule_date else ''} {f'às {schedule_time}' if schedule_time else ''}."
                )

            scheduled_customer = (
                match.get("customer", {}).get("name")
                if isinstance(match.get("customer"), dict)
                else match.get("customer_name") or match.get("customer") or "Cliente"
            )
            tools.delete_schedule(match["id"])
            return (
                f"✓ Agendamento de {scheduled_customer} em "
                f"{match.get('date') if isinstance(match.get('date'), str) else match.get('date').strftime('%d/%m/%Y')} "
                f"às {match.get('time') if isinstance(match.get('time'), str) else match.get('time').strftime('%H:%M')} "
                "foi cancelado com sucesso."
            )

        # Default help
        return (
            "Posso ajudar você a:\n"
            "• Listar horários disponíveis: 'Quais são os horários para 03/03/2026?'\n"
            "• Agendar uma consulta: 'Quero agendar João Silva em 05/03/2026 às 14:00'\n"
            "• Cancelar um agendamento: 'Cancelar Maria Silva em 12/08/2026 às 09:30'\n\n"
            "Como posso ajudá-lo?"
        )

    except HTTPException as exc:
        detail = str(exc.detail).lower()
        if "fora do funcionamento" in detail:
            return (
                "Esse horário está fora do horário de funcionamento. "
                "Escolha outro horário disponível e posso confirmar o agendamento."
            )
        return f"Erro: {exc.detail}"
    except ValueError as e:
        return f"Erro ao processar dados: {str(e)}"
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return "Desculpe, ocorreu um erro. Tente novamente."


# Funções auxiliares para fallback (pattern matching)
def _extract_date(message: str) -> Optional[str]:
    import re

    match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", message)
    return match.group(1) if match else None


def _extract_time(message: str) -> Optional[str]:
    import re

    match = re.search(r"\b(\d{2}:\d{2}(?::\d{2})?)\b", message)
    if not match:
        return None

    value = match.group(1)
    if len(value) == 5:
        return f"{value}:00"
    return value


def _extract_name(message: str) -> Optional[str]:
    import re

    patterns = [
        r"(?:cancelar|excluir|remover|agendar|marcar|nome)\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s'-]{1,40})(?:\s+(?:em|as|às|no|para))",
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