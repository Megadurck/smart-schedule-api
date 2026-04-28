from sqlalchemy import Column, Integer, ForeignKey, Date, Time, Enum as SAEnum, DateTime, Index, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base
from app.enum.schedule_status import ScheduleStatus


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    professional_id = Column(Integer, ForeignKey("professionals.id"), nullable=True, index=True)

    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    status = Column(
        SAEnum(ScheduleStatus, name="schedulestatus"),
        nullable=False,
        default=ScheduleStatus.PENDING,
        server_default=ScheduleStatus.PENDING.value,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    customer = relationship("Customer", back_populates="schedules")
    company = relationship("Company", back_populates="schedules")
    professional = relationship("Professional", back_populates="schedules")

    __table_args__ = (
        # Índice 1: bloqueia duplicidade quando professional_id é informado
        Index(
            "uq_schedule_active_with_professional",
            "company_id", "professional_id", "date", "time",
            unique=True,
            postgresql_where=text(
                "status IN ('pending', 'confirmed') AND professional_id IS NOT NULL"
            ),
        ),
        # Índice 2: bloqueia duplicidade quando professional_id é NULL
        Index(
            "uq_schedule_active_no_professional",
            "company_id", "date", "time",
            unique=True,
            postgresql_where=text(
                "status IN ('pending', 'confirmed') AND professional_id IS NULL"
            ),
        ),
        # Índice auxiliar de performance para consultas por empresa/data/hora
        Index("ix_schedule_company_date_time", "company_id", "date", "time"),
    )
