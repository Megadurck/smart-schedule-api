from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_customer_repo
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerRecord, CustomerUpdate
from app.services import customer_service


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/", response_model=list[CustomerRecord])
def list_customers(
    repo: CustomerRepository = Depends(get_customer_repo),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return customer_service.list_customers(repo, skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerRecord)
def get_customer(customer_id: int, repo: CustomerRepository = Depends(get_customer_repo)):
    return customer_service.get_customer(repo, customer_id)


@router.post("/", response_model=CustomerRecord, status_code=201)
def create_customer(payload: CustomerCreate, repo: CustomerRepository = Depends(get_customer_repo)):
    return customer_service.create_customer(repo, payload.name)


@router.put("/{customer_id}", response_model=CustomerRecord)
def update_customer(customer_id: int, payload: CustomerUpdate, repo: CustomerRepository = Depends(get_customer_repo)):
    return customer_service.update_customer(repo, customer_id, payload.name)


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, repo: CustomerRepository = Depends(get_customer_repo)):
    customer_service.delete_customer(repo, customer_id)
