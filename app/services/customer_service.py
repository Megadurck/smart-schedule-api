from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import customer_repository


def list_customers(db: Session, company_id: int):
    return customer_repository.list_customers(db, company_id)


def get_customer(db: Session, company_id: int, customer_id: int):
    customer = customer_repository.get_customer(db, customer_id, company_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente final nao encontrado")
    return customer


def create_customer(db: Session, company_id: int, name: str):
    existing = customer_repository.get_customer_by_name(db, name, company_id)
    if existing:
        raise HTTPException(status_code=409, detail="Cliente final ja cadastrado")
    return customer_repository.create_customer(db, name, company_id)


def update_customer(db: Session, company_id: int, customer_id: int, name: str):
    customer = customer_repository.get_customer(db, customer_id, company_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente final nao encontrado")

    duplicate = customer_repository.get_customer_by_name(db, name, company_id)
    if duplicate and duplicate.id != customer_id:
        raise HTTPException(status_code=409, detail="Cliente final ja cadastrado")

    return customer_repository.update_customer(db, customer, name)


def delete_customer(db: Session, company_id: int, customer_id: int):
    customer = customer_repository.get_customer(db, customer_id, company_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente final nao encontrado")
    customer_repository.delete_customer(db, customer)
