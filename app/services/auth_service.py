from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories import client_repository


def register_client_credentials(db: Session, client_name: str, password: str):
    client = client_repository.get_client_by_name(db, client_name)

    if client and client.password_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cliente ja possui credenciais cadastradas.",
        )

    password_hash = hash_password(password)

    if client:
        client = client_repository.set_client_password(db, client, password_hash)
    else:
        client = client_repository.create_client(db, client_name, password_hash)

    return _build_token_response(client.name)


def login(db: Session, client_name: str, password: str):
    client = client_repository.get_client_by_name(db, client_name)

    if not client or not client.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )

    if not verify_password(password, client.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )

    return _build_token_response(client.name)


def refresh_access_token(refresh_token: str):
    client_name = decode_token(refresh_token, expected_type="refresh")

    return {
        "access_token": create_access_token(client_name),
        "token_type": "bearer",
        "expires_in": 600,
    }


def get_client_from_access_token(db: Session, token: str):
    client_name = decode_token(token, expected_type="access")
    client = client_repository.get_client_by_name(db, client_name)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cliente nao encontrado para este token.",
        )

    return client


def _build_token_response(client_name: str):
    return {
        "access_token": create_access_token(client_name),
        "refresh_token": create_refresh_token(client_name),
        "token_type": "bearer",
        "expires_in": 600,
    }
