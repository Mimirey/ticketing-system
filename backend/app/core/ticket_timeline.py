from datetime import datetime
from sqlalchemy.orm import Session

from app.models.ticket_history import TicketHistory
from app.models.enums import TicketStatus

def get_ticket_timeline(
        db:Session,
        ticket_id:int,
):
    histories =(
        db.query(TicketHistory)
        .filter(
            TicketHistory.ticket_id == ticket_id,
            TicketHistory.field_changed =="status",
        )
        .order_by(TicketHistory.changed_at.asc())
        .all()
    )

    timeline ={
        "created_at": None,
        "assigned_at": None,
        "in_progress_at":None,
        "qa_at": None,
        "done_at": None
    }
    for history in histories:
        status = history.new_value

        if status == TicketStatus.OPEN.value:
            timeline["created_at"] = history.changed_at
        elif status == TicketStatus.ASSIGNED.value:
            timeline["assigned_at"] = history.changed_at
        elif status == TicketStatus.IN_PROGRESS.value:
            timeline["in_progress_at"] = history.changed_at
        elif status == TicketStatus.QA.value:
            timeline["qa_at"] = history.changed_at
        elif status == TicketStatus.DONE.value:
            timeline["done_at"] = history.changed_at

    return timeline