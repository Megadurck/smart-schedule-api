from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
auth_counter = [0]


def get_auth_headers(company_name: str):
    auth_counter[0] += 1
    payload = {
        "company_name": company_name,
        "user_name": f"dashboard_user_{auth_counter[0]}",
        "password": "senha123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def configure_working_hours(headers):
    response = client.post(
        "/api/v1/working-hours/",
        json={"weekday": 1, "start_time": "08:00:00", "end_time": "18:00:00"},
        headers=headers,
    )
    assert response.status_code == 201


def create_completed_schedule(headers, customer_name: str, time_value: str, professional_id: int | None = None):
    payload = {
        "customer_name": customer_name,
        "date": "03/03/2026",
        "time": time_value,
        "professional_id": professional_id,
    }
    created = client.post("/api/v1/schedule/", json=payload, headers=headers)
    assert created.status_code == 201

    schedule_id = created.json()["id"]
    updated = client.patch(
        f"/api/v1/schedule/{schedule_id}/status",
        json={"status": "completed"},
        headers=headers,
    )
    assert updated.status_code == 200


def test_dashboard_insights_returns_revenue_totals_and_by_professional():
    headers = get_auth_headers("empresa_dashboard_a")
    configure_working_hours(headers)

    professional_response = client.post(
        "/api/v1/professionals/",
        json={"name": "Ana", "is_active": True},
        headers=headers,
    )
    assert professional_response.status_code == 201
    professional_id = professional_response.json()["id"]

    create_completed_schedule(headers, "Cliente 1", "09:00:00", professional_id)
    create_completed_schedule(headers, "Cliente 2", "10:00:00", None)

    company_update = client.put(
        "/api/v1/company-admin/",
        json={
            "display_name": "Empresa Dashboard",
            "cancellation_policy": "Regra",
            "default_timezone": "America/Sao_Paulo",
            "reminder_lead_minutes": 120,
            "average_ticket_amount": 150,
        },
        headers=headers,
    )
    assert company_update.status_code == 200

    response = client.get("/api/v1/dashboard/insights", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert data["schedule_count"] == 2
    assert data["professional_count"] == 1
    assert data["customer_count"] == 2
    assert data["average_ticket_amount"] == 150
    assert data["completed_schedules"] == 2
    assert data["total_revenue"] == 300
    assert len(data["next_schedules"]) == 2

    by_professional = {item["professional_name"]: item for item in data["revenue_by_professional"]}
    assert by_professional["Ana"]["completed_schedules"] == 1
    assert by_professional["Ana"]["total_revenue"] == 150
    assert by_professional["Sem profissional definido"]["completed_schedules"] == 1
    assert by_professional["Sem profissional definido"]["total_revenue"] == 150


def test_dashboard_insights_is_isolated_by_company():
    headers_a = get_auth_headers("empresa_dashboard_isolated_a")
    headers_b = get_auth_headers("empresa_dashboard_isolated_b")

    configure_working_hours(headers_a)
    create_completed_schedule(headers_a, "Cliente A", "11:00:00", None)

    response_b = client.get("/api/v1/dashboard/insights", headers=headers_b)
    assert response_b.status_code == 200

    data = response_b.json()
    assert data["schedule_count"] == 0
    assert data["professional_count"] == 0
    assert data["customer_count"] == 0
    assert data["completed_schedules"] == 0
    assert data["total_revenue"] == 0
    assert data["revenue_by_professional"] == []
    assert data["next_schedules"] == []
