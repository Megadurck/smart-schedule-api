from datetime import timedelta

from fastapi.testclient import TestClient

from app.core import security
from app.main import app


client = TestClient(app)


def test_register_and_login_flow():
    register_payload = {
        "company_name": "empresa_auth",
        "user_name": "usuario_auth",
        "password": "senha123",
    }

    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201
    register_data = register_response.json()
    assert "access_token" in register_data
    assert "refresh_token" in register_data

    login_response = client.post("/api/v1/auth/login", json=register_payload)
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data


def test_register_existing_credentials_returns_conflict():
    payload = {
        "company_name": "empresa_dup",
        "user_name": "usuario_duplicado",
        "password": "senha123",
    }

    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


def test_login_invalid_password():
    payload = {
        "company_name": "empresa_login",
        "user_name": "usuario_login",
        "password": "senha123",
    }
    client.post("/api/v1/auth/register", json=payload)

    bad_login = client.post(
        "/api/v1/auth/login",
        json={
            "company_name": "empresa_login",
            "user_name": "usuario_login",
            "password": "senha_errada",
        },
    )
    assert bad_login.status_code == 401


def test_refresh_and_me_endpoints():
    payload = {
        "company_name": "empresa_me",
        "user_name": "usuario_me",
        "password": "senha123",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    tokens = register_response.json()

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["name"] == "usuario_me"
    assert "company_id" in me_data

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data


def test_expired_access_token_message():
    payload = {
        "company_name": "empresa_expirada",
        "user_name": "usuario_expirado",
        "password": "senha123",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 201

    expired_access = security._create_token(
        subject="1",
        token_type="access",
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_access}"},
    )

    assert response.status_code == 401
    assert "Token expirado" in response.json()["detail"]


def test_expired_refresh_token_message():
    payload = {
        "company_name": "empresa_refresh_expirada",
        "user_name": "usuario_refresh_expirado",
        "password": "senha123",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 201

    expired_refresh = security._create_token(
        subject="1",
        token_type="refresh",
        expires_delta=timedelta(seconds=-1),
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": expired_refresh},
    )

    assert response.status_code == 401
    assert "Faça login novamente" in response.json()["detail"]


def test_same_user_name_in_different_companies_is_allowed():
    payload_a = {
        "company_name": "empresa_a",
        "user_name": "usuario_global",
        "password": "senha123",
    }
    payload_b = {
        "company_name": "empresa_b",
        "user_name": "usuario_global",
        "password": "senha123",
    }

    response_a = client.post("/api/v1/auth/register", json=payload_a)
    response_b = client.post("/api/v1/auth/register", json=payload_b)

    assert response_a.status_code == 201
    assert response_b.status_code == 201
