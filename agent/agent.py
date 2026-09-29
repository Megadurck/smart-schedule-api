"""
Main agent logic - LLM-driven scheduling assistant
"""
import json
import logging
import threading
import time as time_module
import unicodedata
from typing import Optional

from fastapi import HTTPException

from app.core.phone import normalize_whatsapp_phone
from agent.config import AGENT_PROVIDER
from agent import tools

if AGENT_PROVIDER == "ollama":
    from agent.llm import OllamaClient
    from agent.prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)
_PENDING_CANCELLATIONS: dict[str, tuple[int, float]] = {}
_PENDING_CANCELLATIONS_LOCK = threading.Lock()
_CANCELLATION_CONFIRMATION_TTL_SECONDS = 300


CHAT_SYSTEM_PROMPT = (
    "Você é um assistente virtual amigável em português brasileiro. "
    "Converse de forma natural, objetiva e educada. "
    "Não invente acesso a banco, agenda ou sistemas externos."
)


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


def handle_chat_message(message: str) -> str:
    """Temporary chat-only mode (no API/tool calls)."""
    clean_message = (message or "").strip()
    if not clean_message:
        return "Pode me enviar uma mensagem?"

    # Try Ollama first for natural chat. If unavailable, fallback to offline chat.
    try:
        from agent.llm import OllamaClient

        with OllamaClient() as llm:
            return llm.generate(clean_message, system=CHAT_SYSTEM_PROMPT)
    except Exception as exc:  # pragma: no cover
        logger.warning(f"Chat via Ollama indisponivel, usando fallback offline: {exc}")

    text = _compact_text_for_matching(clean_message)
    if any(word in text for word in ["oi", "ola", "olá", "bom dia", "boa tarde", "boa noite"]):
        return "Oi! Estou online e pronto para conversar com você."

    if "quem e voce" in text or "quem é voce" in text:
        return "Sou seu assistente virtual no WhatsApp. Posso conversar normalmente com você."

    return (
        "Entendi. No momento estou em modo conversa, sem consultar a API de agendamentos. "
        "Se quiser, podemos falar sobre qualquer assunto e depois eu volto para o modo agenda."
    )


def parse_intent(message: str) -> dict:
    """Route para diferentes estratégias de parsing"""
    if AGENT_PROVIDER == "ollama":
        parsed = parse_intent_llm(message)
        if parsed.get("action") not in {
            "list_slots",
            "list_my_schedules",
            "create_schedule",
            "delete_schedule",
        }:
            return parse_intent_simple(message)
        return parsed
    else:
        # Fallback para padrão simples se não configurado
        return parse_intent_simple(message)


def _compact_text_for_matching(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def parse_intent_simple(message: str) -> dict:
    """Fallback simples baseado em patterns (original)"""
    text = _compact_text_for_matching(message.strip())

    if any(
        phrase in text
        for phrase in ("meus agendamentos", "listar agendamentos", "minhas consultas")
    ):
        return {"action": "list_my_schedules"}

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


def _is_cancel_confirmation(message: str) -> bool:
    normalized = _compact_text_for_matching(message).strip(" .,!?")
    return normalized in {"confirmar cancelamento", "confirmo cancelamento"}


def _clear_expired_cancellations(now: float) -> None:
    expired = [
        phone
        for phone, (_, expires_at) in _PENDING_CANCELLATIONS.items()
        if expires_at <= now
    ]
    for phone in expired:
        _PENDING_CANCELLATIONS.pop(phone, None)


def _consume_pending_cancellation(whatsapp_phone: str) -> int | None:
    now = time_module.time()
    with _PENDING_CANCELLATIONS_LOCK:
        _clear_expired_cancellations(now)
        pending = _PENDING_CANCELLATIONS.pop(whatsapp_phone, None)
    return pending[0] if pending else None


def _discard_pending_cancellation(whatsapp_phone: str) -> None:
    with _PENDING_CANCELLATIONS_LOCK:
        _PENDING_CANCELLATIONS.pop(whatsapp_phone, None)


def _format_schedule(schedule: dict) -> str:
    schedule_date = schedule["date"]
    schedule_time = schedule["time"]
    date_text = schedule_date.strftime("%d/%m/%Y") if hasattr(schedule_date, "strftime") else str(schedule_date)
    time_text = schedule_time.strftime("%H:%M") if hasattr(schedule_time, "strftime") else str(schedule_time)
    professional = schedule.get("professional")
    professional_text = f" com {professional['name']}" if isinstance(professional, dict) else ""
    return f"{date_text} às {time_text}{professional_text}"


def handle_message(message: str, sender_phone: str | None = None) -> str:
    """Process user message and return response"""
    try:
        whatsapp_phone = normalize_whatsapp_phone(sender_phone)
    except ValueError:
        return "Não consegui identificar seu número de WhatsApp. Envie a mensagem novamente pelo canal da empresa."

    if _is_cancel_confirmation(message):
        if not whatsapp_phone:
            return "Não há cancelamento aguardando confirmação para este número."
        schedule_id = _consume_pending_cancellation(whatsapp_phone)
        if schedule_id is None:
            return "Não há cancelamento aguardando confirmação para este número."
        try:
            tools.cancel_my_schedule(schedule_id, whatsapp_phone)
            logger.info(
                "WhatsApp action completed action=cancel schedule_id=%s sender_phone=%s",
                schedule_id,
                whatsapp_phone,
            )
            return "Agendamento cancelado. O registro foi mantido no histórico da empresa."
        except HTTPException as exc:
            return f"Não foi possível cancelar o agendamento: {exc.detail}"

    if whatsapp_phone:
        _discard_pending_cancellation(whatsapp_phone)

    intent = parse_intent(message)

    try:
        action = intent.get("action")
        confidence = intent.get("confidence", 1.0)

        # Log intent com confidence
        logger.info(f"Intent: {action} (confidence: {confidence:.2f})")

        if action in {"list_my_schedules", "create_schedule", "delete_schedule"} and not whatsapp_phone:
            return "Para consultar, agendar ou cancelar, envie a mensagem pelo WhatsApp da empresa."

        if action == "list_my_schedules":
            schedules = tools.list_my_schedules(whatsapp_phone)
            logger.info(
                "WhatsApp action completed action=list_my_schedules sender_phone=%s count=%s",
                whatsapp_phone,
                len(schedules),
            )
            if not schedules:
                return "Não encontrei agendamentos ativos futuros vinculados a este número."
            return "Seus agendamentos:\n" + "\n".join(
                f"- {_format_schedule(schedule)}" for schedule in schedules
            )

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
                whatsapp_phone=whatsapp_phone,
            )
            logger.info(
                "WhatsApp action completed action=create_schedule schedule_id=%s sender_phone=%s",
                created["id"],
                whatsapp_phone,
            )
            return (
                f"✓ Agendamento confirmado para {created['customer_name']} em "
                f"{created['date'].strftime('%d/%m/%Y')} às {created['time'].strftime('%H:%M')}."
            )

        if action == "delete_schedule":
            schedule_date = intent.get("date")
            schedule_time = intent.get("time")
            schedules = tools.list_my_schedules(whatsapp_phone)
            matches = [
                schedule
                for schedule in schedules
                if (not schedule_date or _format_schedule(schedule).startswith(schedule_date))
                and (
                    not schedule_time
                    or schedule["time"].strftime("%H:%M") == schedule_time[:5]
                )
            ]

            if not schedule_date and not schedule_time:
                if not schedules:
                    return "Não encontrei agendamentos ativos futuros vinculados a este número."
                return (
                    "Para proteger seus dados, escolha o agendamento pela data e hora:\n"
                    + "\n".join(f"- {_format_schedule(schedule)}" for schedule in schedules)
                )
            if len(matches) != 1:
                if not matches:
                    return "Não encontrei um agendamento ativo desse horário vinculado a este número."
                return "Encontrei mais de um agendamento. Informe a data e a hora exatas."

            match = matches[0]
            with _PENDING_CANCELLATIONS_LOCK:
                _clear_expired_cancellations(time_module.time())
                _PENDING_CANCELLATIONS[whatsapp_phone] = (
                    match["id"],
                    time_module.time() + _CANCELLATION_CONFIRMATION_TTL_SECONDS,
                )
            logger.info(
                "WhatsApp action requested action=cancel schedule_id=%s sender_phone=%s",
                match["id"],
                whatsapp_phone,
            )
            return (
                f"Confirme o cancelamento do agendamento de {_format_schedule(match)}. "
                "Responda CONFIRMAR CANCELAMENTO em até 5 minutos."
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
        if "vinculado ao telefone pela equipe" in detail:
            return "Este cadastro precisa ter o WhatsApp vinculado pela equipe antes de agendar."
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