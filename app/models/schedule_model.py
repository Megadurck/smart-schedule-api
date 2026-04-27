from sqlalchemy import Column, Integer, ForeignKey, Date, Time
from sqlalchemy.orm import relationship

from app.database.session import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=True, index=True)

    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)

    customer = relationship("Customer", back_populates="schedules")
    company = relationship("Company", back_populates="schedules")
    professional = relationship("Professional", back_populates="schedules")
