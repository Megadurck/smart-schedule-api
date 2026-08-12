"""
Webhook para integração com o WhatsApp via Twilio.
"""

from fastapi import APIRouter, Request, Response
from fastapi.concurrency import run_in_threadpool

from agent.agent import handle_message
from agent.whatsapp_client import send_whatsapp_message

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


@router.get("/webhook")
def webhook_health_check():
    """Endpoint simples para validar que o webhook está no ar."""
    return {"status": "ok"}


@router.post("/webhook")
async def receive_webhook(request: Request):
    """Recebe mensagens do Twilio, processa com o agent e responde."""
    form = await request.form()
    from_number = (form.get("From") or "").strip()
    body = (form.get("Body") or "").strip()

    if not from_number or not body:
        return Response(status_code=200)

    phone = from_number.replace("whatsapp:", "")
    reply = await run_in_threadpool(handle_message, body)
    await run_in_threadpool(send_whatsapp_message, phone, reply)

    return Response(status_code=200)
