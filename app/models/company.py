from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.session import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    display_name = Column(String, nullable=True)
    cancellation_policy = Column(Text, nullable=True)
    default_timezone = Column(String, nullable=False, default="America/Sao_Paulo")
    reminder_lead_minutes = Column(Integer, nullable=False, default=120)

    users = relationship("User", back_populates="company")
    customers = relationship("Customer", back_populates="company")
    professionals = relationship("Professional", back_populates="company")
    schedules = relationship("Schedule", back_populates="company")
    working_hours = relationship("WorkingHours", back_populates="company")
