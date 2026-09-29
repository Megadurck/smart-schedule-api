from fastapi import HTTPException

from app.repositories.customer_repository import CustomerRepository


def list_customers(repo: CustomerRepository, skip: int = 0, limit: int = 20):
    return repo.list(skip=skip, limit=limit)


def get_customer(repo: CustomerRepository, customer_id: int):
    customer = repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente final nao encontrado")
    return customer


def create_customer(repo: CustomerRepository, name: str, whatsapp_phone: str | None = None):
    if repo.get_by_name(name):
        raise HTTPException(status_code=409, detail="Cliente final ja cadastrado")
    if whatsapp_phone and repo.get_by_whatsapp_phone(whatsapp_phone):
        raise HTTPException(status_code=409, detail="Telefone WhatsApp ja vinculado a outro cliente")
    return repo.create(name, whatsapp_phone)


def update_customer(
    repo: CustomerRepository,
    customer_id: int,
    name: str,
    whatsapp_phone: str | None = None,
):
    customer = repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente final nao encontrado")
    duplicate = repo.get_by_name(name)
    if duplicate and duplicate.id != customer_id:
        raise HTTPException(status_code=409, detail="Cliente final ja cadastrado")
    phone_duplicate = repo.get_by_whatsapp_phone(whatsapp_phone) if whatsapp_phone else None
    if phone_duplicate and phone_duplicate.id != customer_id:
        raise HTTPException(status_code=409, detail="Telefone WhatsApp ja vinculado a outro cliente")
    return repo.update(customer, name, whatsapp_phone)


def delete_customer(repo: CustomerRepository, customer_id: int):
    customer = repo.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente final nao encontrado")
    repo.delete(customer)
