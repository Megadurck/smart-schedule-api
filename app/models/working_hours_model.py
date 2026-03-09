from sqlalchemy import Column, Integer, Time, Boolean
from app.database.session import Base


class WorkingHours (Base):
    __tablename__ = "working_hours"

    id = Column(Integer, primary_key=True, index=True)

    weekday = Column(Integer, nullable=False, index=True)
    # 0 = segunda | 6 = domingo

    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Duração de cada atendimento em minutos (padrão 30)
    slot_duration_minutes = Column(Integer, default=30, nullable=False)
    
    # Pausa de almoço
    lunch_start = Column(Time, nullable=True)  # padrão 12:00:00
    lunch_end = Column(Time, nullable=True)    # padrão 14:00:00

    is_active = Column(Boolean, default=True)