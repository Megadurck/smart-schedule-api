from sqlalchemy.orm import Session

from app.models.customer import Customer


def find_or_create_customer(db: Session, name: str, company_id: int) -> Customer:
    customer = get_customer_by_name(db, name, company_id)
    if customer:
        return customer

    customer = Customer(name=name, company_id=company_id)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer_by_name(db: Session, name: str, company_id: int) -> Customer | None:
    return (
        db.query(Customer)
        .filter(Customer.name == name, Customer.company_id == company_id)
        .first()
    )


def get_customer(db: Session, customer_id: int, company_id: int) -> Customer | None:
    return (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.company_id == company_id)
        .first()
    )


def list_customers(db: Session, company_id: int) -> list[Customer]:
    return (
        db.query(Customer)
        .filter(Customer.company_id == company_id)
        .order_by(Customer.name)
        .all()
    )


def create_customer(db: Session, name: str, company_id: int) -> Customer:
    customer = Customer(name=name, company_id=company_id)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: Customer, name: str) -> Customer:
    customer.name = name
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer: Customer) -> None:
    db.delete(customer)
    db.commit()
