import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
auth_counter = [0]


def get_auth_headers():
    auth_counter[0] += 1
    payload = {
        "client_name": f"auth_wh_{auth_counter[0]}",
        "password": "senha123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


class TestWorkingHours:
    """Testes para gerenciamento de horários de funcionamento"""

    def test_set_working_hours(self):
        """Testa criação de horário de funcionamento"""
        headers = get_auth_headers()
        working_hours = {
            "weekday": 0,  # segunda
            "start_time": "08:00:00",
            "end_time": "17:00:00"
        }
        response = client.post("/api/v1/working-hours/", json=working_hours, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["weekday"] == 0
        assert data["is_active"] is True

    def test_set_multiple_weekdays(self):
        """Testa definição de horários para múltiplos dias"""
        headers = get_auth_headers()
        days = [
            {"weekday": 0, "start_time": "08:00:00", "end_time": "17:00:00"},
            {"weekday": 1, "start_time": "09:00:00", "end_time": "18:00:00"},
            {"weekday": 2, "start_time": "08:00:00", "end_time": "17:00:00"},
            {"weekday": 3, "start_time": "08:00:00", "end_time": "17:00:00"},
            {"weekday": 4, "start_time": "08:00:00", "end_time": "17:00:00"},
        ]
        
        for day in days:
            response = client.post("/api/v1/working-hours/", json=day, headers=headers)
            assert response.status_code == 201
            data = response.json()
            assert data["weekday"] == day["weekday"]

    def test_list_working_hours(self):
        """Testa listagem de horários de funcionamento"""
        headers = get_auth_headers()
        # Criar alguns horários
        client.post("/api/v1/working-hours/", json={
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00"
        }, headers=headers)
        client.post("/api/v1/working-hours/", json={
            "weekday": 1,
            "start_time": "09:00:00",
            "end_time": "18:00:00"
        }, headers=headers)
        
        response = client.get("/api/v1/working-hours/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_update_working_hours(self):
        """Testa atualização de horário de funcionamento"""
        headers = get_auth_headers()
        client.post("/api/v1/working-hours/", json={
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00"
        }, headers=headers)
        
        # Atualizar mesmo dia com novo horário
        update_response = client.post("/api/v1/working-hours/", json={
            "weekday": 0,
            "start_time": "10:00:00",
            "end_time": "19:00:00"
        }, headers=headers)
        assert update_response.status_code == 201

    def test_invalid_weekday(self):
        """Testa rejeição de weekday inválido"""
        headers = get_auth_headers()
        invalid = {
            "weekday": 7,  # inválido (deve ser 0-6)
            "start_time": "08:00:00",
            "end_time": "17:00:00"
        }
        response = client.post("/api/v1/working-hours/", json=invalid, headers=headers)
        assert response.status_code == 422  # Pydantic validation error
        assert "Invalid weekday value: 7" in str(response.json())

    def test_invalid_time_format(self):
        """Testa rejeição de formato de hora inválido"""
        headers = get_auth_headers()
        invalid = {
            "weekday": 0,
            "start_time": "8am",  # inválido
            "end_time": "5pm"     # inválido
        }
        response = client.post("/api/v1/working-hours/", json=invalid, headers=headers)
        assert response.status_code == 400
        assert "Formato de hora inválido" in response.json()["detail"]

    def test_start_time_after_end_time(self):
        """Testa rejeição quando hora inicial é após hora final"""
        headers = get_auth_headers()
        invalid = {
            "weekday": 0,
            "start_time": "17:00:00",
            "end_time": "08:00:00"  # invertido
        }
        response = client.post("/api/v1/working-hours/", json=invalid, headers=headers)
        assert response.status_code == 400
        assert "hora inicial deve ser anterior" in response.json()["detail"]

    def test_start_time_equals_end_time(self):
        """Testa rejeição quando hora inicial é igual à final"""
        headers = get_auth_headers()
        invalid = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "08:00:00"
        }
        response = client.post("/api/v1/working-hours/", json=invalid, headers=headers)
        assert response.status_code == 400

    def test_invalid_lunch_interval(self):
        """Testa rejeição quando hora de início do almoço é após a de fim"""
        headers = get_auth_headers()
        invalid = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00",
            "lunch_start": "14:00:00",
            "lunch_end": "12:00:00"  # invertido
        }
        response = client.post("/api/v1/working-hours/", json=invalid, headers=headers)
        assert response.status_code == 400
        assert "início do almoço deve ser anterior" in response.json()["detail"]

    def test_invalid_lunch_interval_equal(self):
        """Testa rejeição quando hora de início e fim do almoço são iguais"""
        headers = get_auth_headers()
        invalid = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00",
            "lunch_start": "12:00:00",
            "lunch_end": "12:00:00"
        }
        response = client.post("/api/v1/working-hours/", json=invalid, headers=headers)
        assert response.status_code == 400
        assert "início do almoço deve ser anterior" in response.json()["detail"]

    def test_lunch_before_working_hours(self):
        """Testa rejeição quando almoço começa antes do horário de trabalho"""
        headers = get_auth_headers()
        invalid = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00",
            "lunch_start": "07:00:00",  # antes das 08:00
            "lunch_end": "12:00:00"
        }
        response = client.post("/api/v1/working-hours/", json=invalid, headers=headers)
        assert response.status_code == 400
        assert "Horário de almoço deve estar dentro do expediente" in response.json()["detail"]

    def test_lunch_after_working_hours(self):
        """Testa rejeição quando almoço termina após o horário de trabalho"""
        headers = get_auth_headers()
        invalid = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00",
            "lunch_start": "12:00:00",
            "lunch_end": "18:00:00"  # depois das 17:00
        }
        response = client.post("/api/v1/working-hours/", json=invalid, headers=headers)
        assert response.status_code == 400
        assert "Horário de almoço deve estar dentro do expediente" in response.json()["detail"]

    def test_working_hours_with_json(self):
        """Testa se working hours também funciona com JSON"""
        headers = get_auth_headers()
        payload = {
            "weekday": 3,
            "start_time": "08:30:00",
            "end_time": "17:30:00"
        }
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["weekday"] == 3


class TestScheduleWithWorkingHours:
    """Testes para agendamentos com validação de horário de trabalho"""

    def setup_method(self):
        """Setup: configurar horários de funcionamento antes de cada teste"""
        headers = get_auth_headers()
        # Segunda a sexta: 08:00 - 17:00
        for weekday in range(5):  # 0-4 (seg a sex)
            client.post("/api/v1/working-hours/", json={
                "weekday": weekday,
                "start_time": "08:00:00",
                "end_time": "17:00:00"
            }, headers=headers)

    def test_create_schedule_within_working_hours(self):
        """Testa criação de agendamento dentro do horário de funcionamento"""
        headers = get_auth_headers()
        agendamento = {
            "client_name": "João Silva",
            "date": "03/03/2026",
            "time": "10:00:00"
        }
        response = client.post("/api/v1/schedule/", json=agendamento, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["client"]["name"] == "João Silva"

    def test_create_schedule_before_working_hours(self):
        """Testa rejeição de agendamento antes do horário de funcionamento"""
        headers = get_auth_headers()
        agendamento = {
            "client_name": "Maria",
            "date": "03/03/2026",
            "time": "06:00:00"
        }
        response = client.post("/api/v1/schedule/", json=agendamento, headers=headers)
        assert response.status_code == 422
        assert "Horário fora do funcionamento" in response.json()["detail"]

    def test_create_schedule_after_working_hours(self):
        """Testa rejeição de agendamento após o horário de funcionamento"""
        headers = get_auth_headers()
        agendamento = {
            "client_name": "Pedro",
            "date": "03/03/2026",
            "time": "18:00:00"
        }
        response = client.post("/api/v1/schedule/", json=agendamento, headers=headers)
        assert response.status_code == 422
        assert "Horário fora do funcionamento" in response.json()["detail"]

    def test_create_schedule_at_boundary(self):
        """Testa agendamento exatamente no início e fim do horário"""
        headers = get_auth_headers()
        agendamento_inicio = {
            "client_name": "Alice",
            "date": "03/03/2026",
            "time": "08:00:00"
        }
        response = client.post("/api/v1/schedule/", json=agendamento_inicio, headers=headers)
        assert response.status_code == 201
        assert "id" in response.json()

        agendamento_fim = {
            "client_name": "Bob",
            "date": "03/03/2026",
            "time": "17:00:00"
        }
        response = client.post("/api/v1/schedule/", json=agendamento_fim, headers=headers)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_create_schedule_no_working_hours_defined(self):
        """Testa agendamento quando não há horários definidos para o dia"""
        headers = get_auth_headers()
        agendamento = {
            "client_name": "Carlos",
            "date": "08/03/2026",  # sábado
            "time": "10:00:00"
        }
        response = client.post("/api/v1/schedule/", json=agendamento, headers=headers)
        assert response.status_code == 422
        assert "Horário fora do funcionamento" in response.json()["detail"]

    def test_update_schedule_within_working_hours(self):
        """Testa atualização de agendamento para horário válido"""
        headers = get_auth_headers()
        created = client.post("/api/v1/schedule/", json={
            "client_name": "Cliente",
            "date": "03/03/2026",
            "time": "10:00:00"
        }, headers=headers).json()

        updated = {
            "client_name": "Cliente",
            "date": "04/03/2026",
            "time": "14:00:00"
        }
        response = client.put(f"/api/v1/schedule/{created['id']}", json=updated, headers=headers)
        assert response.status_code == 200
        assert response.json()["time"] == "14:00:00"

    def test_update_schedule_outside_working_hours(self):
        """Testa rejeição de atualização para horário inválido"""
        headers = get_auth_headers()
        created = client.post("/api/v1/schedule/", json={
            "client_name": "Cliente",
            "date": "03/03/2026",
            "time": "10:00:00"
        }, headers=headers).json()

        updated = {
            "client_name": "Cliente",
            "date": "04/03/2026",
            "time": "19:00:00"
        }
        response = client.put(f"/api/v1/schedule/{created['id']}", json=updated, headers=headers)
        assert response.status_code == 422
        assert "Horário fora do funcionamento" in response.json()["detail"]

    def test_schedule_with_json_and_working_hours(self):
        """Testa agendamento via JSON com validação de horário"""
        headers = get_auth_headers()
        payload = {
            "client_name": "JSON User",
            "date": "05/03/2026",
            "time": "11:30:00"
        }
        response = client.post("/api/v1/schedule/", json=payload, headers=headers)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_conflict_and_working_hours_validation_order(self):
        """Testa que conflito é detectado antes de validar horário"""
        headers = get_auth_headers()
        first = client.post("/api/v1/schedule/", json={
            "client_name": "Primeiro",
            "date": "03/03/2026",
            "time": "10:00:00"
        }, headers=headers).json()

        conflicting = {
            "client_name": "Conflito",
            "date": "03/03/2026",
            "time": "10:00:00"
        }
        response = client.post("/api/v1/schedule/", json=conflicting, headers=headers)
        assert response.status_code == 409
        assert response.json()["detail"] == "Horário já ocupado"

    def test_available_slots_calculation(self):
        """Testa cálculo de slots disponíveis para um dia"""
        headers = get_auth_headers()
        # garantir que o horário está numa configuração previsível
        client.post("/api/v1/working-hours/", json={
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "18:00:00",
            "slot_duration_minutes": 30,
            "lunch_start": "12:00:00",
            "lunch_end": "14:00:00",
        }, headers=headers)
        # agora o cálculo deve refletir esta configuração fixa
        response = client.get("/api/v1/working-hours/slots/0")
        assert response.status_code == 200
        data = response.json()
        assert data["weekday"] == 0
        assert data["available_slots"] == 16
        assert data["total_available_minutes"] == 480  # 10h - 2h almoço
        assert data["slot_duration_minutes"] == 30
        assert data["total_lunch_minutes"] == 120

    def test_available_slots_custom_duration(self):
        """Testa cálculo com duração customizável"""
        headers = get_auth_headers()
        # Criar horário com slot de 60 minutos
        client.post("/api/v1/working-hours/", json={
            "weekday": 5,  # sábado
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "slot_duration_minutes": 60,
            "lunch_start": "12:00:00",
            "lunch_end": "13:00:00"
        }, headers=headers)
        
        response = client.get("/api/v1/working-hours/slots/5")
        assert response.status_code == 200
        data = response.json()
        # 8h - 1h almoço = 7h = 420 min / 60 = 7 slots
        assert data["available_slots"] == 7
        assert data["slot_duration_minutes"] == 60
        assert data["total_lunch_minutes"] == 60

    def test_available_slots_no_lunch(self):
        """Testa cálculo quando não há pausa de almoço"""
        headers = get_auth_headers()
        client.post("/api/v1/working-hours/", json={
            "weekday": 6,  # domingo
            "start_time": "10:00:00",
            "end_time": "16:00:00",
            "slot_duration_minutes": 30,
            "lunch_start": None,
            "lunch_end": None
        }, headers=headers)
        
        response = client.get("/api/v1/working-hours/slots/6")
        assert response.status_code == 200
        data = response.json()
        # 6h sem pausa = 360 min / 30 = 12 slots
        assert data["available_slots"] == 12
        assert data["total_available_minutes"] == 360

    def test_available_slots_no_working_hours(self):
        """Testa cálculo quando não há horário definido"""
        # usar domingo (6) que nunca é configurado no setup_method
        response = client.get("/api/v1/working-hours/slots/6")
        assert response.status_code == 200
        data = response.json()
        assert data["available_slots"] == 0


def test_set_working_hours_requires_token():
    payload = {
        "weekday": 0,
        "start_time": "08:00:00",
        "end_time": "17:00:00",
    }
    response = client.post("/api/v1/working-hours/", json=payload)
    assert response.status_code == 401


def test_list_working_hours_is_public():
    response = client.get("/api/v1/working-hours/")
    assert response.status_code == 200
