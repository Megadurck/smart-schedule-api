from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import professional_repository


def list_professionals(db: Session, company_id: int):
    return professional_repository.list_professionals(db, company_id)


def get_professional(db: Session, company_id: int, professional_id: int):
    professional = professional_repository.get_professional(db, professional_id, company_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional nao encontrado")
    return professional


def create_professional(db: Session, company_id: int, name: str, is_active: bool = True):
    existing = professional_repository.get_professional_by_name(db, name, company_id)
    if existing:
        raise HTTPException(status_code=409, detail="Profissional ja cadastrado")
    return professional_repository.create_professional(db, company_id, name, is_active)


def update_professional(db: Session, company_id: int, professional_id: int, name: str, is_active: bool):
    professional = professional_repository.get_professional(db, professional_id, company_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional nao encontrado")

    duplicate = professional_repository.get_professional_by_name(db, name, company_id)
    if duplicate and duplicate.id != professional_id:
        raise HTTPException(status_code=409, detail="Profissional ja cadastrado")

    return professional_repository.update_professional(db, professional, name, is_active)


def delete_professional(db: Session, company_id: int, professional_id: int):
    professional = professional_repository.get_professional(db, professional_id, company_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional nao encontrado")
    professional_repository.delete_professional(db, professional)
