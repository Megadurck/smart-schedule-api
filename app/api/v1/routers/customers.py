from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.schemas.customer import CustomerCreate, CustomerRecord, CustomerUpdate
from app.services import customer_service


router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/", response_model=list[CustomerRecord])
def list_customers(db=Depends(get_db), current_user=Depends(get_current_user)):
    return customer_service.list_customers(db, current_user.company_id)


@router.get("/{customer_id}", response_model=CustomerRecord)
def get_customer(customer_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    return customer_service.get_customer(db, current_user.company_id, customer_id)


@router.post("/", response_model=CustomerRecord, status_code=201)
def create_customer(payload: CustomerCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    return customer_service.create_customer(db, current_user.company_id, payload.name)


@router.put("/{customer_id}", response_model=CustomerRecord)
def update_customer(customer_id: int, payload: CustomerUpdate, db=Depends(get_db), current_user=Depends(get_current_user)):
    return customer_service.update_customer(db, current_user.company_id, customer_id, payload.name)


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    customer_service.delete_customer(db, current_user.company_id, customer_id)
