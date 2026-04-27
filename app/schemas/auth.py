from pydantic import BaseModel, Field


class AuthRegister(BaseModel):
    company_name: str
    user_name: str
    password: str = Field(min_length=6)


class AuthLogin(BaseModel):
    company_name: str
    user_name: str
    password: str = Field(min_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 600


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 600
