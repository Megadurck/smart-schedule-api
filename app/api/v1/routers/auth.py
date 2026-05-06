from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.schemas.auth import (
    AccessTokenResponse,
    AuthLogin,
    AuthRegister,
    RefreshTokenRequest,
    TokenResponse,
)
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: AuthRegister, db=Depends(get_db)):
    return auth_service.register_user_credentials(
        db,
        payload.company_name,
        payload.user_name,
        payload.password,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: AuthLogin, db=Depends(get_db)):
    return auth_service.login(
        db,
        payload.company_name,
        payload.user_name,
        payload.password,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(payload: RefreshTokenRequest):
    return auth_service.refresh_access_token(payload.refresh_token)


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    """Retorna os dados do usuário autenticado com base no access token."""
    return {"id": current_user.id, "name": current_user.name, "company_id": current_user.company_id}
