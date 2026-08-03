from sqlalchemy.orm import Session
from app.crud.dashboard import get_dashboard_statistics, get_status_chart, get_priority_chart
from app.schemas.dashboard import DashboardStatisticResponse, StatusChartResponse, PriorityChartResponse
from app.models.user import User

def dashboard_statistics(
    db: Session,
    current_user: User,
):
    stats = get_dashboard_statistics(db, current_user)

    return DashboardStatisticResponse(
        total_ticket=stats.total_ticket or 0,
        open_ticket=stats.open_ticket or 0,
        assigned_ticket=stats.assigned_ticket or 0,
        in_progress_ticket=stats.in_progress_ticket or 0,
        qa_ticket=stats.qa_ticket or 0,
        done_ticket=stats.done_ticket or 0,
        high_priority_ticket=stats.high_priority_ticket or 0,
        medium_priority_ticket=stats.medium_priority_ticket or 0,
        low_priority_ticket=stats.low_priority_ticket or 0,
        critical_priority_ticket=stats.critical_priority_ticket or 0,
    )

def dashboard_status_chart(
    db: Session,
    current_user: User,
):
    data = get_status_chart(db, current_user)

    return [
        StatusChartResponse(
            status=item.status.value,
            count=item.count,
        )
        for item in data
    ]

def dashboard_priority_chart(
    db: Session,
    current_user: User,
):
    data = get_priority_chart(db, current_user)

    return [
        PriorityChartResponse(
            priority=item.priority.value,
            count=item.count,
        )
        for item in data
    ]