from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.schemas.professional import ProfessionalCreate, ProfessionalResponse, ProfessionalUpdate
from app.services import professional_service


router = APIRouter(prefix="/professionals", tags=["Professionals"])


@router.get("/", response_model=list[ProfessionalResponse])
def list_professionals(db=Depends(get_db), current_user=Depends(get_current_user)):
    return professional_service.list_professionals(db, current_user.company_id)


@router.get("/{professional_id}", response_model=ProfessionalResponse)
def get_professional(professional_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    return professional_service.get_professional(db, current_user.company_id, professional_id)


@router.post("/", response_model=ProfessionalResponse, status_code=201)
def create_professional(payload: ProfessionalCreate, db=Depends(get_db), current_user=Depends(get_current_user)):
    return professional_service.create_professional(db, current_user.company_id, payload.name, payload.is_active)


@router.put("/{professional_id}", response_model=ProfessionalResponse)
def update_professional(professional_id: int, payload: ProfessionalUpdate, db=Depends(get_db), current_user=Depends(get_current_user)):
    return professional_service.update_professional(db, current_user.company_id, professional_id, payload.name, payload.is_active)


@router.delete("/{professional_id}", status_code=204)
def delete_professional(professional_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    professional_service.delete_professional(db, current_user.company_id, professional_id)
