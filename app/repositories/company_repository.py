from sqlalchemy.orm import Session

from app.models.company import Company


def get_company_by_name(db: Session, name: str) -> Company | None:
    return db.query(Company).filter(Company.name == name).first()


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
