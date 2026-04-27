from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.professional import Professional


class ProfessionalRepository:
    def __init__(self, db: Session, company_id: int):
        self.db = db
        self.company_id = company_id

    def list(self) -> list[Professional]:
        return (
            self.db.query(Professional)
            .filter(Professional.company_id == self.company_id)
            .order_by(Professional.name)
            .all()
        )

    def get(self, professional_id: int) -> Professional | None:
        return (
            self.db.query(Professional)
            .filter(Professional.id == professional_id, Professional.company_id == self.company_id)
            .one_or_none()
        )

    def get_by_name(self, name: str) -> Professional | None:
        return (
            self.db.query(Professional)
            .filter(Professional.name == name, Professional.company_id == self.company_id)
            .one_or_none()
        )

    def create(self, name: str, is_active: bool = True) -> Professional:
        professional = Professional(company_id=self.company_id, name=name, is_active=is_active)
        self.db.add(professional)
        self.db.commit()
        self.db.refresh(professional)
        return professional

    def update(self, professional: Professional, name: str, is_active: bool) -> Professional:
        professional.name = name
        professional.is_active = is_active
        self.db.commit()
        self.db.refresh(professional)
        return professional

    def delete(self, professional: Professional) -> None:
        self.db.delete(professional)
        self.db.commit()
