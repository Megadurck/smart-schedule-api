from fastapi import HTTPException

from app.repositories.professional_repository import ProfessionalRepository


def list_professionals(repo: ProfessionalRepository, skip: int = 0, limit: int = 20):
    return repo.list(skip=skip, limit=limit)


def get_professional(repo: ProfessionalRepository, professional_id: int):
    professional = repo.get(professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional nao encontrado")
    return professional


def create_professional(repo: ProfessionalRepository, name: str, is_active: bool = True):
    if repo.get_by_name(name):
        raise HTTPException(status_code=409, detail="Profissional ja cadastrado")
    return repo.create(name, is_active)


def update_professional(repo: ProfessionalRepository, professional_id: int, name: str, is_active: bool):
    professional = repo.get(professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional nao encontrado")
    duplicate = repo.get_by_name(name)
    if duplicate and duplicate.id != professional_id:
        raise HTTPException(status_code=409, detail="Profissional ja cadastrado")
    return repo.update(professional, name, is_active)


def delete_professional(repo: ProfessionalRepository, professional_id: int):
    professional = repo.get(professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Profissional nao encontrado")
    repo.delete(professional)
