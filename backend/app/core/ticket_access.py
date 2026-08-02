from fastapi import HTTPException
from app.models.ticket import Ticket
from app.models.user import User

def ensure_ticket_access(current_user: User, ticket: Ticket):
    is_reporter = ticket.reporter_id == current_user.id
    is_pic = ticket.pic_id == current_user.id
    is_pm = current_user.role.name == "PM_IT"

    if not (is_reporter or is_pic or is_pm):
        raise HTTPException(
            status_code=403,
            detail="Kamu tidak punya akses ke ticket ini",
        )