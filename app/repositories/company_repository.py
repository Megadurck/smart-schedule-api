from sqlalchemy.orm import Session

from app.models.company import Company


def get_company_by_name(db: Session, name: str) -> Company | None:
    return db.query(Company).filter(Company.name == name).first()


def get_company_by_id(db: Session, company_id: int) -> Company | None:
    return db.query(Company).filter(Company.id == company_id).first()


def create_company(db: Session, name: str) -> Company:
    company = Company(name=name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def find_or_create_company(db: Session, name: str) -> Company:
    company = get_company_by_name(db, name)
    if company:
        return company

    return create_company(db, name)


def update_company_admin_settings(
    db: Session,
    company: Company,
    display_name: str | None,
    cancellation_policy: str | None,
    default_timezone: str,
    reminder_lead_minutes: int,
    average_ticket_amount: float,
) -> Company:
    company.display_name = display_name
    company.cancellation_policy = cancellation_policy
    company.default_timezone = default_timezone
    company.reminder_lead_minutes = reminder_lead_minutes
    company.average_ticket_amount = average_ticket_amount
    db.add(company)
    db.commit()
    db.refresh(company)
    return company
