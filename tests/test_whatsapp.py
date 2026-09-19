from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
WEBHOOK_SECRET = "test-webhook-secret"


def test_webhook_authenticated_message_is_processed():
    with patch("app.api.v1.routers.whatsapp.handle_message", return_value="Resposta"), patch(
        "app.api.v1.routers.whatsapp.send_whatsapp_message"
    ) as send_message:
        response = client.post(
            "/api/v1/whatsapp/webhook",
            headers={"X-Webhook-Secret": WEBHOOK_SECRET},
            data={"From": "whatsapp:+5511999998888", "Body": "Oi"},
        )

    assert response.status_code == 200
    send_message.assert_called_once_with("+5511999998888", "Resposta")


def test_webhook_without_authentication_is_rejected():
    with patch("app.api.v1.routers.whatsapp.handle_message") as handle_message:
        response = client.post(
            "/api/v1/whatsapp/webhook",
            data={"From": "whatsapp:+5511999998888", "Body": "Oi"},
        )

    assert response.status_code == 401
    handle_message.assert_not_called()


def test_webhook_with_invalid_authentication_is_rejected():
    with patch("app.api.v1.routers.whatsapp.handle_message") as handle_message:
        response = client.post(
            "/api/v1/whatsapp/webhook",
            headers={"X-Webhook-Secret": "wrong-secret"},
            data={"From": "whatsapp:+5511999998888", "Body": "Oi"},
        )

    assert response.status_code == 401
    handle_message.assert_not_called()


def test_webhook_rejects_oversized_payload():
    response = client.post(
        "/api/v1/whatsapp/webhook",
        headers={"X-Webhook-Secret": WEBHOOK_SECRET},
        data={"From": "whatsapp:+5511999998888", "Body": "x" * (16 * 1024)},
    )

    assert response.status_code == 413