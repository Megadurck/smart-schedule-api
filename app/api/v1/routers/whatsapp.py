"""
Webhook para integração com o WhatsApp via Meta Cloud API (WhatsApp Cloud API).
"""
import hashlib
import hmac
import logging

from fastapi import APIRouter, Query, Request, Response
from fastapi.concurrency import run_in_threadpool

from agent.agent import handle_message
from agent.config import META_APP_SECRET, META_VERIFY_TOKEN
from agent.whatsapp_client import send_whatsapp_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_verify_token: str = Query(default="", alias="hub.verify_token"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
):
    """Handshake de verificação exigido pelo Meta ao registrar o webhook."""
    if hub_mode == "subscribe" and META_VERIFY_TOKEN and hub_verify_token == META_VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    return Response(status_code=403)


def _verify_signature(raw_body: bytes, signature_header: str | None) -> bool:
    """Valida a assinatura X-Hub-Signature-256 usando o App Secret do Meta."""
    if not META_APP_SECRET or not signature_header or not signature_header.startswith("sha256="):
        return False

    expected = hmac.new(META_APP_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    received = signature_header.removeprefix("sha256=")
    return hmac.compare_digest(expected, received)


def _extract_message(payload: dict) -> tuple[str, str] | None:
    """Extrai (telefone, texto) da primeira mensagem de texto recebida, se houver."""
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                for message in value.get("messages", []):
                    if message.get("type") == "text":
                        return message["from"], message["text"]["body"]
    except (KeyError, TypeError):
        logger.warning("Payload do WhatsApp em formato inesperado.")
    return None


@router.post("/webhook")
async def receive_webhook(request: Request):
    """Recebe mensagens do WhatsApp, processa com o agent e responde."""
    raw_body = await request.body()

    if not _verify_signature(raw_body, request.headers.get("X-Hub-Signature-256")):
        return Response(status_code=403)

    payload = await request.json()
    extracted = _extract_message(payload)

    if extracted:
        phone, text = extracted
        reply = await run_in_threadpool(handle_message, text)
        await run_in_threadpool(send_whatsapp_message, phone, reply)

    # Meta espera 200 mesmo para eventos ignorados (ex: status de entrega).
    return Response(status_code=200)
