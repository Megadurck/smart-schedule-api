from fastapi import APIRouter, Depends

from app.core.dependencies import get_professional_repo
from app.repositories.professional_repository import ProfessionalRepository
from app.schemas.professional import ProfessionalCreate, ProfessionalResponse, ProfessionalUpdate
from app.services import professional_service


router = APIRouter(prefix="/professionals", tags=["Professionals"])


@router.get("/", response_model=list[ProfessionalResponse])
def list_professionals(repo: ProfessionalRepository = Depends(get_professional_repo)):
    return professional_service.list_professionals(repo)


@router.get("/{professional_id}", response_model=ProfessionalResponse)
def get_professional(professional_id: int, repo: ProfessionalRepository = Depends(get_professional_repo)):
    return professional_service.get_professional(repo, professional_id)


@router.post("/", response_model=ProfessionalResponse, status_code=201)
def create_professional(payload: ProfessionalCreate, repo: ProfessionalRepository = Depends(get_professional_repo)):
    return professional_service.create_professional(repo, payload.name, payload.is_active)


@router.put("/{professional_id}", response_model=ProfessionalResponse)
def update_professional(professional_id: int, payload: ProfessionalUpdate, repo: ProfessionalRepository = Depends(get_professional_repo)):
    return professional_service.update_professional(repo, professional_id, payload.name, payload.is_active)


@router.delete("/{professional_id}", status_code=204)
def delete_professional(professional_id: int, repo: ProfessionalRepository = Depends(get_professional_repo)):
    professional_service.delete_professional(repo, professional_id)
