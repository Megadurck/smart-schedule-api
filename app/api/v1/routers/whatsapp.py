"""
Webhook para integração com o WhatsApp via Neonize.
"""

import hmac
import os

from fastapi import APIRouter, Request, Response
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import HTTPException
from fastapi.concurrency import run_in_threadpool

from agent.agent import handle_message
from agent.whatsapp_client import send_whatsapp_message

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

WEBHOOK_SECRET_ENV = "WHATSAPP_WEBHOOK_SECRET"
WEBHOOK_SECRET_HEADER = "X-Webhook-Secret"
MAX_WEBHOOK_PAYLOAD_BYTES = 16 * 1024


@router.get("/webhook")
def webhook_health_check():
    """Endpoint simples para validar que o webhook está no ar."""
    return {"status": "ok"}


@router.post("/webhook")
async def receive_webhook(request: Request):
    """Recebe mensagens do Neonize, processa com o agent e responde."""
    configured_secret = os.getenv(WEBHOOK_SECRET_ENV, "").strip()
    provided_secret = request.headers.get(WEBHOOK_SECRET_HEADER, "")

    if not configured_secret:
        raise HTTPException(status_code=503, detail="Webhook nao configurado.")
    if not provided_secret or not hmac.compare_digest(provided_secret, configured_secret):
        raise HTTPException(status_code=401, detail="Credencial do webhook invalida.")

    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_WEBHOOK_PAYLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Payload do webhook muito grande.")

    form = await request.form()
    from_number = (form.get("From") or "").strip()
    body = (form.get("Body") or "").strip()

    if len(from_number.encode("utf-8")) + len(body.encode("utf-8")) > MAX_WEBHOOK_PAYLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Payload do webhook muito grande.")

    if not from_number or not body:
        return Response(status_code=200)

    phone = from_number.replace("whatsapp:", "")
    reply = await run_in_threadpool(handle_message, body)
    await run_in_threadpool(send_whatsapp_message, phone, reply)

    return Response(status_code=200)
