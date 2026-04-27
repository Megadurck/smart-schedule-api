from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token_for_company,
    create_refresh_token_for_company,
    decode_token_claims,
    hash_password,
    verify_password,
)
from app.repositories import company_repository, user_repository


def register_user_credentials(
    db: Session,
    company_name: str,
    user_name: str,
    password: str,
):
    company = company_repository.find_or_create_company(db, company_name)
    user = user_repository.get_user_by_name(db, user_name, company.id)

    if user and user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Usuario ja possui credenciais cadastradas.",
        )

    password_hash = hash_password(password)

    if user:
        user = user_repository.set_user_password(db, user, password_hash)
    else:
        user = user_repository.create_user(db, user_name, company.id, password_hash)

    return _build_token_response(user)


def login(db: Session, company_name: str, user_name: str, password: str):
    company = company_repository.get_company_by_name(db, company_name)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )

    user = user_repository.get_user_by_name(db, user_name, company.id)

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas.",
        )

    return _build_token_response(user)


def refresh_access_token(refresh_token: str):
    claims = decode_token_claims(refresh_token, expected_type="refresh")

    return {
        "access_token": create_access_token_for_company(
            subject=claims["subject"],
            company_id=claims["company_id"],
        ),
        "token_type": "bearer",
        "expires_in": 600,
    }


def get_user_from_access_token(db: Session, token: str):
    claims = decode_token_claims(token, expected_type="access")
    user = user_repository.get_user(db, int(claims["subject"]))

    if not user or user.company_id != claims["company_id"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao encontrado para este token.",
        )

    return user


def _build_token_response(user):
    subject = str(user.id)
    return {
        "access_token": create_access_token_for_company(subject, user.company_id),
        "refresh_token": create_refresh_token_for_company(subject, user.company_id),
        "token_type": "bearer",
        "expires_in": 600,
    }
