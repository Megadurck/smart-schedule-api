from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
user_counter = [0]


def get_auth_headers(company_name: str = "empresa_professionals"):
    user_counter[0] += 1
    payload = {
        "company_name": company_name,
        "user_name": f"user_professional_{user_counter[0]}",
        "password": "senha123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def configure_working_hours(headers):
    for weekday in range(5):
        response = client.post(
            "/api/v1/working-hours/",
            json={"weekday": weekday, "start_time": "08:00:00", "end_time": "18:00:00"},
            headers=headers,
        )
        assert response.status_code == 201


def test_professional_crud_flow():
    headers = get_auth_headers()

    created = client.post(
        "/api/v1/professionals/",
        json={"name": "Profissional 1", "is_active": True},
        headers=headers,
    )
    assert created.status_code == 201
    professional_id = created.json()["id"]

    fetched = client.get(f"/api/v1/professionals/{professional_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Profissional 1"

    updated = client.put(
        f"/api/v1/professionals/{professional_id}",
        json={"name": "Profissional 1B", "is_active": False},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["is_active"] is False

    listed = client.get("/api/v1/professionals/", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(f"/api/v1/professionals/{professional_id}", headers=headers)
    assert deleted.status_code == 204


def test_schedule_can_reference_professional():
    headers = get_auth_headers()
    configure_working_hours(headers)

    professional = client.post(
        "/api/v1/professionals/",
        json={"name": "Atendente", "is_active": True},
        headers=headers,
    )
    assert professional.status_code == 201
    professional_id = professional.json()["id"]

    schedule = client.post(
        "/api/v1/schedule/",
        json={
            "customer_name": "Cliente Prof",
            "date": "03/03/2026",
            "time": "09:00:00",
            "professional_id": professional_id,
        },
        headers=headers,
    )
    assert schedule.status_code == 201
    data = schedule.json()
    assert data["professional"]["id"] == professional_id
    assert data["professional"]["name"] == "Atendente"


def test_foreign_professional_is_rejected():
    headers_a = get_auth_headers("empresa_prof_a")
    headers_b = get_auth_headers("empresa_prof_b")
    configure_working_hours(headers_a)

    professional = client.post(
        "/api/v1/professionals/",
        json={"name": "Prof A", "is_active": True},
        headers=headers_b,
    )
    assert professional.status_code == 201
    professional_id = professional.json()["id"]

    schedule = client.post(
        "/api/v1/schedule/",
        json={
            "customer_name": "Cliente A",
            "date": "03/03/2026",
            "time": "09:00:00",
            "professional_id": professional_id,
        },
        headers=headers_a,
    )
    assert schedule.status_code == 404
    assert schedule.json()["detail"] == "Profissional nao encontrado"
