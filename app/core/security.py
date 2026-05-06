from datetime import datetime, timedelta, timezone
import os

from fastapi import HTTPException, status
from dotenv import load_dotenv
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext


load_dotenv()

# SECRET_KEY deve ser definida como variável de ambiente. Nunca versionar este valor.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não definida. Configure a variável de ambiente SECRET_KEY.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_DAYS = 7

# pbkdf2_sha256 é mais seguro que bcrypt para ataques de força bruta em servidores modernos.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Função base usada apenas internamente e pelos testes de token expirado.
# Não carrega company_id — use create_token_with_company para produção.
def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_token_with_company(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    company_id: int,
) -> str:
    """Gera um JWT com o company_id embutido, garantindo o isolamento multi-tenant.

    O company_id é verificado em cada requisição autenticada pelo middleware
    get_current_user → get_user_from_access_token.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,          # ID do usuário (user.id como string)
        "type": token_type,       # "access" ou "refresh"
        "company_id": company_id, # chave de isolamento multi-tenant
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token_for_company(subject: str, company_id: int) -> str:
    """Cria um access token de curta duração (10 min) com company_id."""
    return create_token_with_company(
        subject=subject,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        company_id=company_id,
    )


def create_refresh_token_for_company(subject: str, company_id: int) -> str:
    """Cria um refresh token de longa duração (7 dias) com company_id."""
    return create_token_with_company(
        subject=subject,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        company_id=company_id,
    )


def decode_token_claims(token: str, expected_type: str) -> dict:
    """Decodifica e valida um JWT, retornando {'subject', 'company_id'}.

    Garante que o token é do tipo correto e carrega o company_id,
    impedindo que um token de uma empresa seja aceito por outra.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError as exc:
        if expected_type == "access":
            detail = "Token expirado. Use refresh para renovar ou faça login novamente."
        else:
            detail = "Refresh token expirado. Faça login novamente."
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail) from exc
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        ) from exc

    subject = payload.get("sub")
    token_type = payload.get("type")
    company_id = payload.get("company_id")

    if not subject or token_type != expected_type or company_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        )

    return {"subject": str(subject), "company_id": int(company_id)}
