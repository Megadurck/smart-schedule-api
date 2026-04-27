from sqlalchemy import Column, Integer, ForeignKey, Date, Time, Enum as SAEnum, DateTime
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
