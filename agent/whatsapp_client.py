import logging
import os

from twilio.rest import Client

logger = logging.getLogger(__name__)


def send_whatsapp_message(to: str, body: str) -> None:
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    from_number = os.getenv("TWILIO_WHATSAPP_FROM", "").strip()

    if not account_sid or not auth_token or not from_number:
        logger.error("Twilio nao configurado; mensagem nao enviada.")
        return

    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            body=body,
            from_=from_number,
            to=f"whatsapp:{to}"
        )
        logger.info("Mensagem enviada via Twilio WhatsApp.")
    except Exception as exc:
        logger.error(f"Falha ao enviar mensagem via Twilio: {exc}")