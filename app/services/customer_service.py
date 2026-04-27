from fastapi import HTTPException

from app.repositories.customer_repository import CustomerRepository


def list_customers(repo: CustomerRepository):
    return repo.list()


def get_customer(repo: CustomerRepository, customer_id: int):
    customer = repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente final nao encontrado")
    return customer


def create_customer(repo: CustomerRepository, name: str):
    if repo.get_by_name(name):
        raise HTTPException(status_code=409, detail="Cliente final ja cadastrado")
    return repo.create(name)


def update_customer(repo: CustomerRepository, customer_id: int, name: str):
    customer = repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente final nao encontrado")
    duplicate = repo.get_by_name(name)
    if duplicate and duplicate.id != customer_id:
        raise HTTPException(status_code=409, detail="Cliente final ja cadastrado")
    return repo.update(customer, name)


def delete_customer(repo: CustomerRepository, customer_id: int):
    customer = repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente final nao encontrado")
    repo.delete(customer)
