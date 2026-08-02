from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.dependencies import get_db, get_current_user
from app.schemas.dashboard import DashboardStatisticResponse, StatusChartResponse, PriorityChartResponse
from app.services.dashboard import dashboard_statistics, dashboard_status_chart, dashboard_priority_chart

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)
@router.get(
    "/statistics",
    response_model=DashboardStatisticResponse,
)
def get_dashboard_statistics_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return dashboard_statistics(
        db=db,
        current_user=current_user,
    )

@router.get(
    "/chart/status",
    response_model=List[StatusChartResponse],
)
def get_status_chart_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return dashboard_status_chart(
        db=db,
        current_user=current_user,
    )

@router.get(
    "/chart/priority",
    response_model=List[PriorityChartResponse],
)
def get_priority_chart_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return dashboard_priority_chart(
        db=db,
        current_user=current_user,
    )