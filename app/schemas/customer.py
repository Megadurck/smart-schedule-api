from pydantic import BaseModel


class CustomerCreate(BaseModel):
    name: str


class CustomerUpdate(BaseModel):
    name: str


class CustomerRecord(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
