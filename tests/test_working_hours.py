from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
auth_counter = [0]


def get_auth_headers(company_name: str = "empresa_wh"):
    auth_counter[0] += 1
    payload = {
        "company_name": company_name,
        "user_name": f"auth_wh_{auth_counter[0]}",
        "password": "senha123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    access_token = response.json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}


class TestWorkingHours:
    def test_set_working_hours(self):
        headers = get_auth_headers()
        payload = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00",
        }
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["weekday"] == 0
        assert data["is_active"] is True

    def test_set_multiple_weekdays(self):
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
        headers = get_auth_headers()
        client.post(
            "/api/v1/working-hours/",
            json={"weekday": 0, "start_time": "08:00:00", "end_time": "17:00:00"},
            headers=headers,
        )
        client.post(
            "/api/v1/working-hours/",
            json={"weekday": 1, "start_time": "09:00:00", "end_time": "18:00:00"},
            headers=headers,
        )

        response = client.get("/api/v1/working-hours/", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_update_working_hours(self):
        headers = get_auth_headers()
        client.post(
            "/api/v1/working-hours/",
            json={"weekday": 0, "start_time": "08:00:00", "end_time": "17:00:00"},
            headers=headers,
        )

        update_response = client.post(
            "/api/v1/working-hours/",
            json={"weekday": 0, "start_time": "10:00:00", "end_time": "19:00:00"},
            headers=headers,
        )
        assert update_response.status_code == 201

    def test_invalid_weekday(self):
        headers = get_auth_headers()
        payload = {"weekday": 7, "start_time": "08:00:00", "end_time": "17:00:00"}
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 422
        assert "Invalid weekday value: 7" in str(response.json())

    def test_invalid_time_format(self):
        headers = get_auth_headers()
        payload = {"weekday": 0, "start_time": "8am", "end_time": "5pm"}
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 400
        assert "Formato de hora inválido" in response.json()["detail"]

    def test_start_time_after_end_time(self):
        headers = get_auth_headers()
        payload = {"weekday": 0, "start_time": "17:00:00", "end_time": "08:00:00"}
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 400
        assert "hora inicial deve ser anterior" in response.json()["detail"]

    def test_start_time_equals_end_time(self):
        headers = get_auth_headers()
        payload = {"weekday": 0, "start_time": "08:00:00", "end_time": "08:00:00"}
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 400

    def test_invalid_lunch_interval(self):
        headers = get_auth_headers()
        payload = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00",
            "lunch_start": "14:00:00",
            "lunch_end": "12:00:00",
        }
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 400
        assert "início do almoço deve ser anterior" in response.json()["detail"]

    def test_invalid_lunch_interval_equal(self):
        headers = get_auth_headers()
        payload = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00",
            "lunch_start": "12:00:00",
            "lunch_end": "12:00:00",
        }
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 400
        assert "início do almoço deve ser anterior" in response.json()["detail"]

    def test_lunch_before_working_hours(self):
        headers = get_auth_headers()
        payload = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00",
            "lunch_start": "07:00:00",
            "lunch_end": "12:00:00",
        }
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 400
        assert "Horário de almoço deve estar dentro do expediente" in response.json()["detail"]

    def test_lunch_after_working_hours(self):
        headers = get_auth_headers()
        payload = {
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "17:00:00",
            "lunch_start": "12:00:00",
            "lunch_end": "18:00:00",
        }
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 400
        assert "Horário de almoço deve estar dentro do expediente" in response.json()["detail"]

    def test_working_hours_with_json(self):
        headers = get_auth_headers()
        payload = {"weekday": 3, "start_time": "08:30:00", "end_time": "17:30:00"}
        response = client.post("/api/v1/working-hours/", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["weekday"] == 3


class TestScheduleWithWorkingHours:
    def setup_method(self):
        self.headers = get_auth_headers("empresa_sched_wh")
        for weekday in range(5):
            response = client.post(
                "/api/v1/working-hours/",
                json={"weekday": weekday, "start_time": "08:00:00", "end_time": "17:00:00"},
                headers=self.headers,
            )
            assert response.status_code == 201

    def test_create_schedule_within_working_hours(self):
        payload = {"customer_name": "Joao Silva", "date": "03/03/2026", "time": "10:00:00"}
        response = client.post("/api/v1/schedule/", json=payload, headers=self.headers)
        assert response.status_code == 201
        assert response.json()["customer"]["name"] == "Joao Silva"

    def test_create_schedule_before_working_hours(self):
        payload = {"customer_name": "Maria", "date": "03/03/2026", "time": "06:00:00"}
        response = client.post("/api/v1/schedule/", json=payload, headers=self.headers)
        assert response.status_code == 422
        assert "Horário fora do funcionamento" in response.json()["detail"]

    def test_create_schedule_after_working_hours(self):
        payload = {"customer_name": "Pedro", "date": "03/03/2026", "time": "18:00:00"}
        response = client.post("/api/v1/schedule/", json=payload, headers=self.headers)
        assert response.status_code == 422
        assert "Horário fora do funcionamento" in response.json()["detail"]

    def test_create_schedule_at_boundary(self):
        start_payload = {"customer_name": "Alice", "date": "03/03/2026", "time": "08:00:00"}
        end_payload = {"customer_name": "Bob", "date": "03/03/2026", "time": "17:00:00"}

        response_start = client.post("/api/v1/schedule/", json=start_payload, headers=self.headers)
        response_end = client.post("/api/v1/schedule/", json=end_payload, headers=self.headers)

        assert response_start.status_code == 201
        assert response_end.status_code == 201

    def test_create_schedule_no_working_hours_defined(self):
        payload = {"customer_name": "Carlos", "date": "08/03/2026", "time": "10:00:00"}
        response = client.post("/api/v1/schedule/", json=payload, headers=self.headers)
        assert response.status_code == 422
        assert "Horário fora do funcionamento" in response.json()["detail"]

    def test_update_schedule_within_working_hours(self):
        created = client.post(
            "/api/v1/schedule/",
            json={"customer_name": "Cliente", "date": "03/03/2026", "time": "10:00:00"},
            headers=self.headers,
        ).json()

        updated = {"customer_name": "Cliente", "date": "04/03/2026", "time": "14:00:00"}
        response = client.put(f"/api/v1/schedule/{created['id']}", json=updated, headers=self.headers)
        assert response.status_code == 200
        assert response.json()["time"] == "14:00:00"

    def test_update_schedule_outside_working_hours(self):
        created = client.post(
            "/api/v1/schedule/",
            json={"customer_name": "Cliente", "date": "03/03/2026", "time": "10:00:00"},
            headers=self.headers,
        ).json()

        updated = {"customer_name": "Cliente", "date": "04/03/2026", "time": "19:00:00"}
        response = client.put(f"/api/v1/schedule/{created['id']}", json=updated, headers=self.headers)
        assert response.status_code == 422
        assert "Horário fora do funcionamento" in response.json()["detail"]

    def test_schedule_with_json_and_working_hours(self):
        payload = {"customer_name": "JSON User", "date": "05/03/2026", "time": "11:30:00"}
        response = client.post("/api/v1/schedule/", json=payload, headers=self.headers)
        assert response.status_code == 201
        assert "id" in response.json()

    def test_conflict_and_working_hours_validation_order(self):
        client.post(
            "/api/v1/schedule/",
            json={"customer_name": "Primeiro", "date": "03/03/2026", "time": "10:00:00"},
            headers=self.headers,
        )

        payload = {"customer_name": "Conflito", "date": "03/03/2026", "time": "10:00:00"}
        response = client.post("/api/v1/schedule/", json=payload, headers=self.headers)
        assert response.status_code == 409
        assert response.json()["detail"] == "Horário já ocupado"

    def test_available_slots_calculation(self):
        client.post(
            "/api/v1/working-hours/",
            json={
                "weekday": 0,
                "start_time": "08:00:00",
                "end_time": "18:00:00",
                "slot_duration_minutes": 30,
                "lunch_start": "12:00:00",
                "lunch_end": "14:00:00",
            },
            headers=self.headers,
        )

        response = client.get("/api/v1/working-hours/slots", params={"date": "02/03/2026"}, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["weekday"] == 0
        assert data["date"] == "02/03/2026"
        assert data["available_slots"] == 16
        assert data["total_available_minutes"] == 480
        assert data["slot_duration_minutes"] == 30
        assert data["lunch_duration_minutes"] == 120
        assert data["total_lunch_minutes"] == 120
        assert data["booked_slots"] == 0
        assert data["total_slots"] == 16

    def test_available_slots_custom_duration(self):
        client.post(
            "/api/v1/working-hours/",
            json={
                "weekday": 5,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
                "slot_duration_minutes": 60,
                "lunch_start": "12:00:00",
                "lunch_end": "13:00:00",
            },
            headers=self.headers,
        )

        response = client.get("/api/v1/working-hours/slots", params={"date": "07/03/2026"}, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["available_slots"] == 7
        assert data["slot_duration_minutes"] == 60
        assert data["lunch_duration_minutes"] == 60
        assert data["total_lunch_minutes"] == 60
        assert data["booked_slots"] == 0
        assert data["total_slots"] == 7

    def test_available_slots_no_lunch(self):
        client.post(
            "/api/v1/working-hours/",
            json={
                "weekday": 6,
                "start_time": "10:00:00",
                "end_time": "16:00:00",
                "slot_duration_minutes": 30,
                "lunch_start": None,
                "lunch_end": None,
            },
            headers=self.headers,
        )

        response = client.get("/api/v1/working-hours/slots", params={"date": "08/03/2026"}, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["available_slots"] == 12
        assert data["total_available_minutes"] == 360
        assert data["lunch_duration_minutes"] == 0
        assert data["booked_slots"] == 0
        assert data["total_slots"] == 12

    def test_available_slots_no_working_hours(self):
        response = client.get("/api/v1/working-hours/slots", params={"date": "08/03/2026"}, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["date"] == "08/03/2026"
        assert data["weekday"] == 6
        assert data["available_slots"] == 0

    def test_available_slots_subtracts_booked_active_schedules(self):
        client.post(
            "/api/v1/working-hours/",
            json={
                "weekday": 3,
                "start_time": "08:00:00",
                "end_time": "18:00:00",
                "slot_duration_minutes": 30,
                "lunch_start": "12:00:00",
                "lunch_end": "13:00:00",
            },
            headers=self.headers,
        )

        for payload in [
            {"customer_name": "Cliente 1", "date": "30/04/2026", "time": "08:00:00"},
            {"customer_name": "Cliente 2", "date": "30/04/2026", "time": "08:30:00"},
        ]:
            response = client.post("/api/v1/schedule/", json=payload, headers=self.headers)
            assert response.status_code == 201

        response = client.get("/api/v1/working-hours/slots", params={"date": "30/04/2026"}, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["weekday"] == 3
        assert data["total_slots"] == 18
        assert data["booked_slots"] == 2
        assert data["available_slots"] == 16
        assert data["total_available_minutes"] == 480

    def test_available_slots_ignores_cancelled_schedule(self):
        client.post(
            "/api/v1/working-hours/",
            json={
                "weekday": 3,
                "start_time": "08:00:00",
                "end_time": "18:00:00",
                "slot_duration_minutes": 30,
                "lunch_start": "12:00:00",
                "lunch_end": "13:00:00",
            },
            headers=self.headers,
        )

        created = client.post(
            "/api/v1/schedule/",
            json={"customer_name": "Cliente Cancelado", "date": "30/04/2026", "time": "08:00:00"},
            headers=self.headers,
        )
        assert created.status_code == 201

        cancelled = client.patch(
            f"/api/v1/schedule/{created.json()['id']}/status",
            json={"status": "cancelled"},
            headers=self.headers,
        )
        assert cancelled.status_code == 200

        response = client.get("/api/v1/working-hours/slots", params={"date": "30/04/2026"}, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["booked_slots"] == 0
        assert data["available_slots"] == 18
        assert data["total_available_minutes"] == 540

    def test_available_slots_invalid_date_format(self):
        response = client.get("/api/v1/working-hours/slots", params={"date": "2026-03-02"}, headers=self.headers)
        assert response.status_code == 400
        assert response.json()["detail"] == "Formato de data inválido. Use DD/MM/YYYY"


def test_set_working_hours_requires_token():
    payload = {"weekday": 0, "start_time": "08:00:00", "end_time": "17:00:00"}
    response = client.post("/api/v1/working-hours/", json=payload)
    assert response.status_code == 401


def test_list_working_hours_requires_token():
    response = client.get("/api/v1/working-hours/")
    assert response.status_code == 401


def test_working_hours_isolated_between_companies():
    headers_a = get_auth_headers("empresa_hours_a")
    headers_b = get_auth_headers("empresa_hours_b")

    client.post(
        "/api/v1/working-hours/",
        json={
            "weekday": 0,
            "start_time": "08:00:00",
            "end_time": "12:00:00",
            "lunch_start": None,
            "lunch_end": None,
        },
        headers=headers_a,
    )
    client.post(
        "/api/v1/working-hours/",
        json={
            "weekday": 0,
            "start_time": "13:00:00",
            "end_time": "18:00:00",
            "lunch_start": None,
            "lunch_end": None,
        },
        headers=headers_b,
    )

    list_a = client.get("/api/v1/working-hours/", headers=headers_a).json()
    list_b = client.get("/api/v1/working-hours/", headers=headers_b).json()

    assert len(list_a) == 1
    assert len(list_b) == 1
    assert list_a[0]["start_time"] == "08:00:00"
    assert list_b[0]["start_time"] == "13:00:00"
