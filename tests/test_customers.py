from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
user_counter = [0]


def get_auth_headers(company_name: str = "empresa_customers"):
    user_counter[0] += 1
    payload = {
        "company_name": company_name,
        "user_name": f"user_customer_{user_counter[0]}",
        "password": "senha123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_customer_crud_flow():
    headers = get_auth_headers()

    created = client.post("/api/v1/customers/", json={"name": "Cliente Final"}, headers=headers)
    assert created.status_code == 201
    customer_id = created.json()["id"]

    fetched = client.get(f"/api/v1/customers/{customer_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Cliente Final"

    updated = client.put(
        f"/api/v1/customers/{customer_id}",
        json={"name": "Cliente Final Atualizado"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Cliente Final Atualizado"

    listed = client.get("/api/v1/customers/", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    deleted = client.delete(f"/api/v1/customers/{customer_id}", headers=headers)
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/customers/{customer_id}", headers=headers)
    assert missing.status_code == 404


def test_customer_is_isolated_by_company():
    headers_a = get_auth_headers("empresa_a")
    headers_b = get_auth_headers("empresa_b")

    response = client.post("/api/v1/customers/", json={"name": "Cliente Compartilhado"}, headers=headers_a)
    assert response.status_code == 201
    customer_id = response.json()["id"]

    foreign = client.get(f"/api/v1/customers/{customer_id}", headers=headers_b)
    assert foreign.status_code == 404
