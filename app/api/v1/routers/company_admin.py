from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_company_id
from app.database.session import get_db
from app.schemas.company_admin import (
    CompanyAdminSettingsResponse,
    CompanyAdminSettingsUpdate,
)
from app.services import company_admin_service


router = APIRouter(prefix="/company-admin", tags=["Company Admin"])


@router.get("/", response_model=CompanyAdminSettingsResponse)
def get_company_admin(
    db: Session = Depends(get_db),
    company_id: int = Depends(get_company_id),
):
    return company_admin_service.get_company_admin_settings(db, company_id)


@router.put("/", response_model=CompanyAdminSettingsResponse)
def update_company_admin(
    payload: CompanyAdminSettingsUpdate,
    db: Session = Depends(get_db),
    company_id: int = Depends(get_company_id),
):
    return company_admin_service.update_company_admin_settings(
        db,
        company_id=company_id,
        display_name=payload.display_name,
        cancellation_policy=payload.cancellation_policy,
        default_timezone=payload.default_timezone,
        reminder_lead_minutes=payload.reminder_lead_minutes,
    )
