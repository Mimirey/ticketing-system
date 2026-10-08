from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.report import TicketReportResponse
from app.services.report import get_ticket_report
from app.core.dependencies import require_role

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

@router.get(
    "/tickets",
    response_model=TicketReportResponse,
)
def ticket_report(
    start_date: date = Query(...),
    end_date: date = Query(...),
    staff_ids: list[int] | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("PM_IT")),
):
    return get_ticket_report(
        db=db,
        start_date=start_date,
        end_date=end_date,
        staff_ids=staff_ids,
    )