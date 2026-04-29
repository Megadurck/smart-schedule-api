from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import company_repository


def get_company_admin_settings(db: Session, company_id: int):
    company = company_repository.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")

    return {
        "company_id": company.id,
        "company_name": company.name,
        "display_name": company.display_name,
        "cancellation_policy": company.cancellation_policy,
        "default_timezone": company.default_timezone,
        "reminder_lead_minutes": company.reminder_lead_minutes,
    }


def update_company_admin_settings(
    db: Session,
    company_id: int,
    display_name: str | None,
    cancellation_policy: str | None,
    default_timezone: str,
    reminder_lead_minutes: int,
):
    company = company_repository.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa nao encontrada")

    updated = company_repository.update_company_admin_settings(
        db,
        company,
        display_name=display_name,
        cancellation_policy=cancellation_policy,
        default_timezone=default_timezone,
        reminder_lead_minutes=reminder_lead_minutes,
    )

    return {
        "company_id": updated.id,
        "company_name": updated.name,
        "display_name": updated.display_name,
        "cancellation_policy": updated.cancellation_policy,
        "default_timezone": updated.default_timezone,
        "reminder_lead_minutes": updated.reminder_lead_minutes,
    }
