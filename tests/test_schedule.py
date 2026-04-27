import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
counter = [0]
auth_counter = [0]


def get_auth_headers(company_name: str = "empresa_schedule"):
    auth_counter[0] += 1
    payload = {
        "company_name": company_name,
        "user_name": f"auth_schedule_{auth_counter[0]}",
        "password": "senha123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(autouse=True)
def setup_working_hours():
    headers = get_auth_headers("empresa_schedule")
    for weekday in range(5):
        response = client.post(
            "/api/v1/working-hours/",
            json={
                "weekday": weekday,
                "start_time": "08:00:00",
                "end_time": "18:00:00",
            },
            headers=headers,
        )
        assert response.status_code == 201


def create_schedule(headers=None):
    counter[0] += 1
    headers = headers or get_auth_headers("empresa_schedule")
    minute = counter[0] % 60
    payload = {
        "customer_name": f"Cliente{counter[0]}",
        "date": "03/03/2026",
        "time": f"10:{minute:02d}:00",
    }
    response = client.post("/api/v1/schedule/", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_create_schedule():
    data = create_schedule()
    assert data["id"] is not None
    assert data["customer"]["name"].startswith("Cliente")


def test_read_schedule():
    headers = get_auth_headers("empresa_schedule")
    created = create_schedule(headers=headers)
    response = client.get(f"/api/v1/schedule/{created['id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["customer"]["name"].startswith("Cliente")
    assert data["date"] == "2026-03-03"
    assert data["time"].startswith("10:")


def test_create_schedule_json():
    headers = get_auth_headers("empresa_schedule")
    payload = {"customer_name": "JsonUser", "date": "03/03/2026", "time": "09:00:00"}
    response = client.post("/api/v1/schedule/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["customer"]["name"] == "JsonUser"


def test_update_schedule_json():
    headers = get_auth_headers("empresa_schedule")
    created = create_schedule(headers=headers)
    updated = {"customer_name": "JsonEdit", "date": "04/03/2026", "time": "11:00:00"}
    response = client.put(f"/api/v1/schedule/{created['id']}", json=updated, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["customer"]["name"] == "JsonEdit"
    assert data["date"] == "2026-03-04"
    assert data["time"] == "11:00:00"


def test_update_schedule():
    headers = get_auth_headers("empresa_schedule")
    created = create_schedule(headers=headers)
    updated_data = {
        "customer_name": "Maria",
        "date": "04/03/2026",
        "time": "14:00:00",
    }
    response = client.put(f"/api/v1/schedule/{created['id']}", json=updated_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["customer"]["name"] == "Maria"
    assert data["date"] == "2026-03-04"
    assert data["time"] == "14:00:00"


def test_delete_schedule():
    headers = get_auth_headers("empresa_schedule")
    created = create_schedule(headers=headers)
    response = client.delete(f"/api/v1/schedule/{created['id']}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/api/v1/schedule/{created['id']}", headers=headers)
    assert response.status_code == 404


def test_create_schedule_invalid_data():
    headers = get_auth_headers("empresa_schedule")
    invalid_payload = {"customer_name": "Joao"}
    response = client.post("/api/v1/schedule/", data=invalid_payload, headers=headers)
    assert response.status_code == 422


def test_read_nonexistent_schedule():
    headers = get_auth_headers("empresa_schedule")
    response = client.get("/api/v1/schedule/99999", headers=headers)
    assert response.status_code == 404


def test_list_schedules():
    headers = get_auth_headers("empresa_schedule")
    create_schedule(headers=headers)
    create_schedule(headers=headers)
    response = client.get("/api/v1/schedule/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    for item in data:
        assert "id" in item
        assert "customer" in item
        assert "date" in item
        assert "time" in item


def test_create_schedule_invalid_format():
    headers = get_auth_headers("empresa_schedule")
    bad = {"customer_name": "Bob", "date": "2026-02-27", "time": "3pm"}
    response = client.post("/api/v1/schedule/", json=bad, headers=headers)
    assert response.status_code == 400
    assert "Formato de data ou hora inválido" in response.json()["detail"]


def test_create_schedule_invalid_format_json():
    headers = get_auth_headers("empresa_schedule")
    bad = {"customer_name": "Bob", "date": "2026-02-27", "time": "3pm"}
    response = client.post("/api/v1/schedule/", json=bad, headers=headers)
    assert response.status_code == 400
    assert "Formato de data ou hora inválido" in response.json()["detail"]


def test_update_schedule_conflict():
    headers = get_auth_headers("empresa_schedule")
    a = create_schedule(headers=headers)
    b = create_schedule(headers=headers)

    payload = {
        "customer_name": "Outro",
        "date": "03/03/2026",
        "time": a["time"],
    }
    response = client.put(f"/api/v1/schedule/{b['id']}", json=payload, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Horário já ocupado"

    b2 = create_schedule(headers=headers)
    response = client.put(f"/api/v1/schedule/{b2['id']}", json=payload, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Horário já ocupado"


def test_schedule_conflict():
    headers = get_auth_headers("empresa_schedule")
    first = {
        "customer_name": "Joao Conflito",
        "date": "27/02/2026",
        "time": "15:00:00",
    }
    response1 = client.post("/api/v1/schedule/", json=first, headers=headers)
    assert response1.status_code == 201

    second = {
        "customer_name": "Maria Conflito",
        "date": "27/02/2026",
        "time": "15:00:00",
    }
    response2 = client.post("/api/v1/schedule/", json=second, headers=headers)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Horário já ocupado"


def test_create_schedule_requires_token():
    payload = {
        "customer_name": "SemToken",
        "date": "03/03/2026",
        "time": "10:00:00",
    }
    response = client.post("/api/v1/schedule/", json=payload)
    assert response.status_code == 401


def test_list_schedule_requires_token():
    response = client.get("/api/v1/schedule/")
    assert response.status_code == 401


def test_suggest_schedule_prefers_recurring_history():
    headers = get_auth_headers("empresa_schedule")
    payload_1 = {"customer_name": "Cliente Recorrente", "date": "03/03/2026", "time": "10:00:00"}
    payload_2 = {"customer_name": "Cliente Recorrente", "date": "10/03/2026", "time": "10:00:00"}
    response_1 = client.post("/api/v1/schedule/", json=payload_1, headers=headers)
    response_2 = client.post("/api/v1/schedule/", json=payload_2, headers=headers)
    assert response_1.status_code == 201
    assert response_2.status_code == 201

    suggestion_request = {
        "customer_name": "Cliente Recorrente",
        "start_date": "11/03/2026",
        "limit": 3,
        "search_days": 30,
    }
    suggestion_response = client.post(
        "/api/v1/schedule/suggestions", json=suggestion_request, headers=headers
    )

    assert suggestion_response.status_code == 200
    data = suggestion_response.json()
    assert data["customer_name"] == "Cliente Recorrente"
    assert len(data["suggestions"]) >= 1
    assert data["suggestions"][0]["time"] == "10:00:00"
    assert data["suggestions"][0]["date"] == "2026-03-17"
    assert data["suggestions"][0]["source"] == "history_preference"


def test_suggest_schedule_falls_back_to_next_available_without_history():
    headers = get_auth_headers("empresa_schedule")
    suggestion_request = {
        "customer_name": "Cliente Novo",
        "start_date": "02/03/2026",
        "limit": 2,
        "search_days": 14,
    }

    suggestion_response = client.post(
        "/api/v1/schedule/suggestions", json=suggestion_request, headers=headers
    )

    assert suggestion_response.status_code == 200
    data = suggestion_response.json()
    assert data["customer_name"] == "Cliente Novo"
    assert len(data["suggestions"]) == 2
    assert data["suggestions"][0]["source"] == "next_available"
    assert data["suggestions"][0]["date"] == "2026-03-02"


def test_schedule_isolated_between_companies():
    headers_a = get_auth_headers("empresa_a")
    headers_b = get_auth_headers("empresa_b")

    for headers in (headers_a, headers_b):
        response = client.post(
            "/api/v1/working-hours/",
            json={
                "weekday": 4,
                "start_time": "08:00:00",
                "end_time": "18:00:00",
            },
            headers=headers,
        )
        assert response.status_code == 201

    first = {
        "customer_name": "Cliente A",
        "date": "27/02/2026",
        "time": "16:00:00",
    }
    second = {
        "customer_name": "Cliente B",
        "date": "27/02/2026",
        "time": "16:00:00",
    }

    response_a = client.post("/api/v1/schedule/", json=first, headers=headers_a)
    response_b = client.post("/api/v1/schedule/", json=second, headers=headers_b)

    assert response_a.status_code == 201
    assert response_b.status_code == 201
