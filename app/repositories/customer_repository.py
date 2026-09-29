from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session, company_id: int):
        self.db = db
        self.company_id = company_id

    def find_or_create(self, name: str, whatsapp_phone: str | None = None) -> Customer:
        if whatsapp_phone:
            customer = self.get_by_whatsapp_phone(whatsapp_phone)
            if customer:
                return customer

            name_match = self.get_by_name(name)
            if name_match:
                raise ValueError(
                    "Cadastro existente precisa ser vinculado ao telefone pela equipe."
                )

        else:
            customer = self.get_by_name(name)
            if customer:
                return customer
        customer = Customer(name=name, company_id=self.company_id, whatsapp_phone=whatsapp_phone)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_by_whatsapp_phone(self, whatsapp_phone: str) -> Customer | None:
        return (
            self.db.query(Customer)
            .filter(
                Customer.whatsapp_phone == whatsapp_phone,
                Customer.company_id == self.company_id,
            )
            .one_or_none()
        )

    def get_by_name(self, name: str) -> Customer | None:
        return (
            self.db.query(Customer)
            .filter(Customer.name == name, Customer.company_id == self.company_id)
            .one_or_none()
        )

    def get(self, customer_id: int) -> Customer | None:
        return (
            self.db.query(Customer)
            .filter(Customer.id == customer_id, Customer.company_id == self.company_id)
            .one_or_none()
        )

    def list(self, skip: int = 0, limit: int = 20) -> list[Customer]:
        return (
            self.db.query(Customer)
            .filter(Customer.company_id == self.company_id)
            .order_by(Customer.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, name: str, whatsapp_phone: str | None = None) -> Customer:
        customer = Customer(
            name=name,
            company_id=self.company_id,
            whatsapp_phone=whatsapp_phone,
        )
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(self, customer: Customer, name: str, whatsapp_phone: str | None) -> Customer:
        customer.name = name
        customer.whatsapp_phone = whatsapp_phone
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> None:
        self.db.delete(customer)
        self.db.commit()
