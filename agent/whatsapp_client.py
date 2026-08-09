"""
Client for sending outbound messages via the Meta WhatsApp Cloud API.
"""
import logging

import httpx

from agent.config import (
    META_API_VERSION,
    META_PHONE_NUMBER_ID,
    META_WHATSAPP_TOKEN,
)

logger = logging.getLogger(__name__)


def send_whatsapp_message(to: str, body: str) -> None:
    """Envia uma mensagem de texto para o número informado via Graph API."""
    if not META_WHATSAPP_TOKEN or not META_PHONE_NUMBER_ID:
        logger.error(
            "META_WHATSAPP_TOKEN ou META_PHONE_NUMBER_ID nao configurados; "
            "mensagem nao enviada."
        )
        return

    url = f"https://graph.facebook.com/{META_API_VERSION}/{META_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    headers = {"Authorization": f"Bearer {META_WHATSAPP_TOKEN}"}

    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.error(
            f"Falha ao enviar mensagem WhatsApp ({exc.response.status_code}): "
            f"{exc.response.text}"
        )
    except httpx.HTTPError as exc:
        logger.error(f"Falha ao enviar mensagem WhatsApp: {exc}")
