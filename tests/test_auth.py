from datetime import timedelta

from fastapi.testclient import TestClient

from app.core import security
from app.main import app


client = TestClient(app)


def test_register_and_login_flow():
    register_payload = {
        "client_name": "cliente_auth",
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
        "client_name": "cliente_duplicado",
        "password": "senha123",
    }

    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


def test_login_invalid_password():
    payload = {
        "client_name": "cliente_login",
        "password": "senha123",
    }
    client.post("/api/v1/auth/register", json=payload)

    bad_login = client.post(
        "/api/v1/auth/login",
        json={"client_name": "cliente_login", "password": "senha_errada"},
    )
    assert bad_login.status_code == 401


def test_refresh_and_me_endpoints():
    payload = {
        "client_name": "cliente_me",
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
    assert me_data["name"] == "cliente_me"

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data


def test_expired_access_token_message():
    payload = {
        "client_name": "cliente_expirado",
        "password": "senha123",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 201

    expired_access = security._create_token(
        subject="cliente_expirado",
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
        "client_name": "cliente_refresh_expirado",
        "password": "senha123",
    }
    register_response = client.post("/api/v1/auth/register", json=payload)
    assert register_response.status_code == 201

    expired_refresh = security._create_token(
        subject="cliente_refresh_expirado",
        token_type="refresh",
        expires_delta=timedelta(seconds=-1),
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": expired_refresh},
    )

    assert response.status_code == 401
    assert "Faça login novamente" in response.json()["detail"]
