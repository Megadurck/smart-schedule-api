from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
_user_counter = 0


def _auth_headers(company_name: str) -> dict[str, str]:
    global _user_counter
    _user_counter += 1
    payload = {
        "company_name": company_name,
        "user_name": f"whatsapp_owner_{_user_counter}",
        "password": "senha123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _next_date() -> date:
    today = date.today()
    return today + timedelta(days=1)


def _configure_hours(headers: dict[str, str]) -> None:
    for weekday in range(7):
        response = client.post(
            "/api/v1/working-hours/",
            json={
                "weekday": weekday,
                "start_time": "08:00:00",
                "end_time": "12:00:00",
                "lunch_start": None,
                "lunch_end": None,
            },
            headers=headers,
        )
        assert response.status_code == 201


def test_team_can_link_existing_customer_and_phone_is_unique_per_company():
    headers = _auth_headers("empresa_vinculo_whatsapp")
    _configure_hours(headers)
    created = client.post(
        "/api/v1/customers/",
        json={"name": "Cliente existente"},
        headers=headers,
    )
    assert created.status_code == 201
    schedule = client.post(
        "/api/v1/schedule/",
        json={
            "customer_name": "Cliente existente",
            "date": _next_date().strftime("%d/%m/%Y"),
            "time": "09:00:00",
        },
        headers=headers,
    )
    assert schedule.status_code == 201

    before_link = client.post(
        "/api/v1/schedule/mine",
        json={"whatsapp_phone": "5511999998888"},
        headers=headers,
    )
    assert before_link.status_code == 200
    assert before_link.json() == []

    linked = client.put(
        f"/api/v1/customers/{created.json()['id']}",
        json={
            "name": "Cliente existente",
            "whatsapp_phone": "+55 (11) 99999-8888",
        },
        headers=headers,
    )
    assert linked.status_code == 200
    assert linked.json()["whatsapp_phone"] == "5511999998888"

    after_link = client.post(
        "/api/v1/schedule/mine",
        json={"whatsapp_phone": "5511999998888"},
        headers=headers,
    )
    assert [item["id"] for item in after_link.json()] == [schedule.json()["id"]]

    duplicate = client.post(
        "/api/v1/customers/",
        json={"name": "Outro cliente", "whatsapp_phone": "5511999998888"},
        headers=headers,
    )
    assert duplicate.status_code == 409


def test_whatsapp_booking_is_visible_and_cancellable_only_by_linked_phone():
    headers = _auth_headers("empresa_agenda_whatsapp")
    other_company_headers = _auth_headers("outra_empresa_agenda_whatsapp")
    _configure_hours(headers)
    schedule_date = _next_date()
    phone = "5511999998888"

    created = client.post(
        "/api/v1/schedule/",
        json={
            "customer_name": "Cliente WhatsApp",
            "date": schedule_date.strftime("%d/%m/%Y"),
            "time": "09:30:00",
            "whatsapp_phone": phone,
        },
        headers=headers,
    )
    assert created.status_code == 201
    schedule_id = created.json()["id"]

    own = client.post(
        "/api/v1/schedule/mine",
        json={"whatsapp_phone": "+55 11 99999-8888"},
        headers=headers,
    )
    assert own.status_code == 200
    assert [item["id"] for item in own.json()] == [schedule_id]

    other_phone = client.post(
        "/api/v1/schedule/mine",
        json={"whatsapp_phone": "5511888887777"},
        headers=headers,
    )
    assert other_phone.status_code == 200
    assert other_phone.json() == []

    other_company = client.post(
        "/api/v1/schedule/mine",
        json={"whatsapp_phone": phone},
        headers=other_company_headers,
    )
    assert other_company.status_code == 200
    assert other_company.json() == []

    forbidden_cancel = client.post(
        f"/api/v1/schedule/{schedule_id}/cancel-mine",
        json={"whatsapp_phone": "5511888887777"},
        headers=headers,
    )
    assert forbidden_cancel.status_code == 404

    cancelled = client.post(
        f"/api/v1/schedule/{schedule_id}/cancel-mine",
        json={"whatsapp_phone": phone},
        headers=headers,
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"

    no_longer_active = client.post(
        "/api/v1/schedule/mine",
        json={"whatsapp_phone": phone},
        headers=headers,
    )
    assert no_longer_active.json() == []


def test_whatsapp_booking_does_not_claim_unlinked_customer_by_name():
    headers = _auth_headers("empresa_nao_reivindicar_cliente")
    _configure_hours(headers)
    existing = client.post(
        "/api/v1/customers/",
        json={"name": "Maria Silva"},
        headers=headers,
    )
    assert existing.status_code == 201

    response = client.post(
        "/api/v1/schedule/",
        json={
            "customer_name": "Maria Silva",
            "date": _next_date().strftime("%d/%m/%Y"),
            "time": "09:30:00",
            "whatsapp_phone": "5511999998888",
        },
        headers=headers,
    )
    assert response.status_code == 409
    assert "vinculado ao telefone pela equipe" in response.json()["detail"]