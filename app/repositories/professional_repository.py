from sqlalchemy.orm import Session

from app.models.professional import Professional


def list_professionals(db: Session, company_id: int) -> list[Professional]:
    return (
        db.query(Professional)
        .filter(Professional.company_id == company_id)
        .order_by(Professional.name)
        .all()
    )


def get_professional(db: Session, professional_id: int, company_id: int) -> Professional | None:
    return (
        db.query(Professional)
        .filter(Professional.id == professional_id, Professional.company_id == company_id)
        .first()
    )


def get_professional_by_name(db: Session, name: str, company_id: int) -> Professional | None:
    return (
        db.query(Professional)
        .filter(Professional.name == name, Professional.company_id == company_id)
        .first()
    )


def create_professional(db: Session, company_id: int, name: str, is_active: bool = True) -> Professional:
    professional = Professional(company_id=company_id, name=name, is_active=is_active)
    db.add(professional)
    db.commit()
    db.refresh(professional)
    return professional


def update_professional(db: Session, professional: Professional, name: str, is_active: bool) -> Professional:
    professional.name = name
    professional.is_active = is_active
    db.commit()
    db.refresh(professional)
    return professional


def delete_professional(db: Session, professional: Professional) -> None:
    db.delete(professional)
    db.commit()
