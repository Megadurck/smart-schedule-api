import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

counter = [0]
auth_counter = [0]


def get_auth_headers():
    auth_counter[0] += 1
    payload = {
        "client_name": f"auth_schedule_{auth_counter[0]}",
        "password": "senha123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(autouse=True)
def setup_working_hours():
    """Setup: configurar horários de funcionamento antes de cada teste"""
    headers = get_auth_headers()
    # Segunda a sexta: 08:00 - 18:00
    for weekday in range(5):  # 0-4 (seg a sex)
        client.post("/api/v1/working-hours/", json={
            "weekday": weekday,
            "start_time": "08:00:00",
            "end_time": "18:00:00"
        }, headers=headers)


def create_schedule():
    counter[0] += 1
    headers = get_auth_headers()
    agendamento = {
        "client_name": f"João{counter[0]}",  # Nomes únicos para evitar conflitos
        "date": "03/03/2026",  # segundo-feira
        "time": f"10:{counter[0]:02d}:00"
    }
    response = client.post("/api/v1/schedule/", json=agendamento, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    return data


def test_create_schedule():
    data = create_schedule()
    assert data['id'] is not None
    assert data['client']['name'].startswith("João")  # Verifica se o cliente foi criado


def test_read_schedule():
    created = create_schedule()
    response = client.get(f"/api/v1/schedule/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["client"]["name"].startswith("João")
    assert data["date"] == "2026-03-03"  # Data retornada em ISO
    assert data["time"].startswith("10:")


def test_create_schedule_json():
    """Teste criação de agendamento via JSON"""
    headers = get_auth_headers()
    payload = {"client_name": "JsonUser", "date": "03/03/2026", "time": "09:00:00"}
    response = client.post("/api/v1/schedule/", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["client"]["name"] == "JsonUser"


def test_update_schedule_json():
    """Teste atualização de agendamento via JSON"""
    headers = get_auth_headers()
    created = create_schedule()
    updated = {"client_name": "JsonEdit", "date": "04/03/2026", "time": "11:00:00"}
    response = client.put(f"/api/v1/schedule/{created['id']}", json=updated, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["client"]["name"] == "JsonEdit"
    assert data["date"] == "2026-03-04"
    assert data["time"] == "11:00:00"


def test_update_schedule():
    """Teste atualização de agendamento"""
    headers = get_auth_headers()
    created = create_schedule()
    updated_data = {
        "client_name": "Maria",
        "date": "04/03/2026",
        "time": "14:00:00"
    }
    # PUT usando JSON
    response = client.put(f"/api/v1/schedule/{created['id']}", json=updated_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["client"]["name"] == "Maria"
    assert data["date"] == "2026-03-04"
    assert data["time"] == "14:00:00"


def test_delete_schedule():
    headers = get_auth_headers()
    created = create_schedule()
    response = client.delete(f"/api/v1/schedule/{created['id']}", headers=headers)
    assert response.status_code == 204
    
    # Verifica que foi deletado
    response = client.get(f"/api/v1/schedule/{created['id']}")
    assert response.status_code == 404


def test_create_schedule_invalid_data():
    headers = get_auth_headers()
    invalid_agendamento = {"client_name": "João"}
    response = client.post("/api/v1/schedule/", data=invalid_agendamento, headers=headers)
    assert response.status_code == 422  # Unprocessable Entity devido a campos faltantes


def test_read_nonexistent_schedule():
    response = client.get("/api/v1/schedule/99999")
    assert response.status_code == 404


def test_list_schedules():
    # Criar alguns agendamentos
    create_schedule()
    create_schedule()
    response = client.get("/api/v1/schedule/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # Pelo menos os criados
    for item in data:
        assert "id" in item
        assert "client" in item
        assert "date" in item
        assert "time" in item


def test_create_schedule_invalid_format():
    """Teste formatação inválida de data/hora"""
    headers = get_auth_headers()
    bad = {"client_name": "Bob", "date": "2026-02-27", "time": "3pm"}
    response = client.post("/api/v1/schedule/", json=bad, headers=headers)
    assert response.status_code == 400
    assert "Formato de data ou hora inválido" in response.json()["detail"]


def test_create_schedule_invalid_format_json():
    """Teste formatação inválida de data/hora via JSON"""
    headers = get_auth_headers()
    bad = {"client_name": "Bob", "date": "2026-02-27", "time": "3pm"}
    response = client.post("/api/v1/schedule/", json=bad, headers=headers)
    assert response.status_code == 400
    assert "Formato de data ou hora inválido" in response.json()["detail"]


def test_update_schedule_conflict():
    """Teste rejeição de atualização com conflito de horário"""
    headers = get_auth_headers()
    # Cria dois agendamentos em horários diferentes
    a = create_schedule()
    b = create_schedule()
    # Tenta atualizar B para o horário de A
    payload = {
        "client_name": "Outro",
        "date": "03/03/2026",  # Mesmo dia de A
        "time": a["time"]
    }
    response = client.put(f"/api/v1/schedule/{b['id']}", json=payload, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Horário já ocupado"

    # Repetir com outro agendamento
    b2 = create_schedule()
    response = client.put(f"/api/v1/schedule/{b2['id']}", json=payload, headers=headers)
    assert response.status_code == 409
    assert response.json()["detail"] == "Horário já ocupado"


def test_schedule_conflict():
    """Teste rejeição quando tenta agendar na mesma data/hora"""
    headers = get_auth_headers()
    agendamento1 = {
        "client_name": "João Conflito",
        "date": "27/02/2026",
        "time": "15:00:00"
    }
    response1 = client.post("/api/v1/schedule/", json=agendamento1, headers=headers)
    assert response1.status_code == 201

    # Tentar criar segundo no mesmo horário
    agendamento2 = {
        "client_name": "Maria Conflito",
        "date": "27/02/2026",
        "time": "15:00:00"
    }
    response2 = client.post("/api/v1/schedule/", json=agendamento2, headers=headers)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Horário já ocupado"


def test_create_schedule_requires_token():
    payload = {
        "client_name": "SemToken",
        "date": "03/03/2026",
        "time": "10:00:00",
    }
    response = client.post("/api/v1/schedule/", json=payload)
    assert response.status_code == 401


def test_list_schedule_is_public():
    response = client.get("/api/v1/schedule/")
    assert response.status_code == 200


def test_suggest_schedule_prefers_recurring_history():
    headers = get_auth_headers()
    # Histórico recorrente: duas terças no mesmo horário para o mesmo cliente.
    payload_1 = {"client_name": "Cliente Recorrente", "date": "03/03/2026", "time": "10:00:00"}
    payload_2 = {"client_name": "Cliente Recorrente", "date": "10/03/2026", "time": "10:00:00"}
    response_1 = client.post("/api/v1/schedule/", json=payload_1, headers=headers)
    response_2 = client.post("/api/v1/schedule/", json=payload_2, headers=headers)
    assert response_1.status_code == 201
    assert response_2.status_code == 201

    # Próxima terça após 11/03/2026 é 17/03/2026.
    suggestion_request = {
        "client_name": "Cliente Recorrente",
        "start_date": "11/03/2026",
        "limit": 3,
        "search_days": 30,
    }
    suggestion_response = client.post(
        "/api/v1/schedule/suggestions", json=suggestion_request, headers=headers
    )

    assert suggestion_response.status_code == 200
    data = suggestion_response.json()
    assert data["client_name"] == "Cliente Recorrente"
    assert len(data["suggestions"]) >= 1
    assert data["suggestions"][0]["time"] == "10:00:00"
    assert data["suggestions"][0]["date"] == "2026-03-17"
    assert data["suggestions"][0]["source"] == "history_preference"


def test_suggest_schedule_falls_back_to_next_available_without_history():
    headers = get_auth_headers()
    suggestion_request = {
        "client_name": "Cliente Novo",
        "start_date": "02/03/2026",
        "limit": 2,
        "search_days": 14,
    }

    suggestion_response = client.post(
        "/api/v1/schedule/suggestions", json=suggestion_request, headers=headers
    )

    assert suggestion_response.status_code == 200
    data = suggestion_response.json()
    assert data["client_name"] == "Cliente Novo"
    assert len(data["suggestions"]) == 2
    assert data["suggestions"][0]["source"] == "next_available"
    assert data["suggestions"][0]["date"] == "2026-03-02"

    