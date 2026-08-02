from sqlalchemy.orm import Session
from app.models.ticket_history import TicketHistory

def log_history(
    db: Session,
    ticket_id: int,
    changed_by_id: int,
    field_changed: str,
    old_value: str | None,
    new_value: str,
):
    entry = TicketHistory(
        ticket_id=ticket_id,
        changed_by_id=changed_by_id,
        field_changed=field_changed,
        old_value=old_value,
        new_value=new_value,
    )
    db.add(entry)
