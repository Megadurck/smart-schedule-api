from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database.session import get_db
from app.services import auth_service


security = HTTPBearer()


def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
):
    return auth_service.get_client_from_access_token(db, credentials.credentials)
