from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.session import Base


class Professional(Base):
    __tablename__ = "professionals"
    __table_args__ = (UniqueConstraint("company_id", "name", name="uq_professional_company_name"),)

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    company = relationship("Company", back_populates="professionals")
    schedules = relationship("Schedule", back_populates="professional")
