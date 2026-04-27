from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.customer_repository import CustomerRepository
from app.repositories.professional_repository import ProfessionalRepository
from app.repositories.schedule_repository import ScheduleRepository
from app.repositories.working_hours_repository import WorkingHoursRepository
from app.services import auth_service


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    return auth_service.get_user_from_access_token(db, credentials.credentials)


def get_company_id(current_user=Depends(get_current_user)) -> int:
    return current_user.company_id


def get_customer_repo(
    db: Session = Depends(get_db),
    company_id: int = Depends(get_company_id),
) -> CustomerRepository:
    return CustomerRepository(db, company_id)


def get_professional_repo(
    db: Session = Depends(get_db),
    company_id: int = Depends(get_company_id),
) -> ProfessionalRepository:
    return ProfessionalRepository(db, company_id)


def get_schedule_repo(
    db: Session = Depends(get_db),
    company_id: int = Depends(get_company_id),
) -> ScheduleRepository:
    return ScheduleRepository(db, company_id)


def get_working_hours_repo(
    db: Session = Depends(get_db),
    company_id: int = Depends(get_company_id),
) -> WorkingHoursRepository:
    return WorkingHoursRepository(db, company_id)


class ScheduleBundle:
    """Agrupa todos os repositórios necessários para operações de agendamento."""

    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        customer_repo: CustomerRepository,
        professional_repo: ProfessionalRepository,
        working_hours_repo: WorkingHoursRepository,
    ):
        self.schedules = schedule_repo
        self.customers = customer_repo
        self.professionals = professional_repo
        self.working_hours = working_hours_repo


def get_schedule_bundle(
    schedule_repo: ScheduleRepository = Depends(get_schedule_repo),
    customer_repo: CustomerRepository = Depends(get_customer_repo),
    professional_repo: ProfessionalRepository = Depends(get_professional_repo),
    working_hours_repo: WorkingHoursRepository = Depends(get_working_hours_repo),
) -> ScheduleBundle:
    return ScheduleBundle(schedule_repo, customer_repo, professional_repo, working_hours_repo)
