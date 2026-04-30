from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_company_id
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import DashboardInsightsResponse
from app.services import dashboard_service


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/insights", response_model=DashboardInsightsResponse)
def get_dashboard_insights(
    start_date: str | None = Query(default=None, description="Formato DD/MM/YYYY"),
    end_date: str | None = Query(default=None, description="Formato DD/MM/YYYY"),
    db: Session = Depends(get_db),
    company_id: int = Depends(get_company_id),
):
    repository = DashboardRepository(db=db, company_id=company_id)
    return dashboard_service.get_dashboard_insights(
        repository=repository,
        start_date=start_date,
        end_date=end_date,
    )
