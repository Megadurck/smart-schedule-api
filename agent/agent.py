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
elif AGENT_PROVIDER == "openai":
    from agent.openai_client import OpenAIClient

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
        return parse_intent_llm(message)
    else:
        # Fallback para padrão simples se não configurado
        return parse_intent_simple(message)


def parse_intent_simple(message: str) -> dict:
    """Fallback simples baseado em patterns (original)"""
    text = message.strip().lower()

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
            slots = tools.list_available_slots(
                start_date=intent.get("date"),
                days_ahead=7,
                limit=8,
            )
            if not slots:
                return "Não encontrei horários disponíveis no período informado."

            human_slots = ", ".join(
                f"{item['date'].strftime('%d/%m/%Y')} {item['time'].strftime('%H:%M')}"
                for item in slots
            )
            return f"Horários disponíveis: {human_slots}"

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

        # Default help
        return (
            "Posso ajudar você a:\n"
            "• Listar horários disponíveis: 'Quais são os horários para 03/03/2026?'\n"
            "• Agendar uma consulta: 'Quero agendar João Silva em 05/03/2026 às 14:00'\n\n"
            "Como posso ajudá-lo?"
        )

    except HTTPException as exc:
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