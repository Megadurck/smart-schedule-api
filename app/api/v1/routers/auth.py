from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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
security = HTTPBearer()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: AuthRegister, db=Depends(get_db)):
    return auth_service.register_client_credentials(db, payload.client_name, payload.password)


@router.post("/login", response_model=TokenResponse)
def login(payload: AuthLogin, db=Depends(get_db)):
    return auth_service.login(db, payload.client_name, payload.password)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(payload: RefreshTokenRequest):
    return auth_service.refresh_access_token(payload.refresh_token)


@router.get("/me")
def me(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)):
    client = auth_service.get_client_from_access_token(db, credentials.credentials)
    return {"id": client.id, "name": client.name}
