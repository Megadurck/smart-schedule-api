from pydantic import BaseModel
from pydantic import field_validator

from app.core.phone import normalize_whatsapp_phone


class CustomerCreate(BaseModel):
    name: str
    whatsapp_phone: str | None = None

    @field_validator("whatsapp_phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        return normalize_whatsapp_phone(value)


class CustomerUpdate(BaseModel):
    name: str
    whatsapp_phone: str | None = None

    @field_validator("whatsapp_phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        return normalize_whatsapp_phone(value)


class CustomerRecord(BaseModel):
    id: int
    name: str
    whatsapp_phone: str | None = None

    model_config = {"from_attributes": True}
