from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    def __init__(self, db: Session, company_id: int):
        self.db = db
        self.company_id = company_id

    def find_or_create(self, name: str) -> Customer:
        customer = self.get_by_name(name)
        if customer:
            return customer
        customer = Customer(name=name, company_id=self.company_id)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

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

    def list(self) -> list[Customer]:
        return (
            self.db.query(Customer)
            .filter(Customer.company_id == self.company_id)
            .order_by(Customer.name)
            .all()
        )

    def create(self, name: str) -> Customer:
        customer = Customer(name=name, company_id=self.company_id)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(self, customer: Customer, name: str) -> Customer:
        customer.name = name
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> None:
        self.db.delete(customer)
        self.db.commit()
