from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.ticket import Ticket
from app.models.enums import TicketStatus, TicketPriority


def get_dashboard_statistics(
    db: Session,
    current_user: User,
):
    query = db.query(
        func.count(Ticket.id).label("total_ticket"),
        func.sum(
            case(
                (Ticket.status == TicketStatus.OPEN, 1),
                else_=0,
            )
        ).label("open_ticket"),
        func.sum(
            case(
                (Ticket.status == TicketStatus.ASSIGNED, 1),
                else_=0,
            )
        ).label("assigned_ticket"),
        func.sum(
            case(
                (Ticket.status == TicketStatus.IN_PROGRESS, 1),
                else_=0,
            )
        ).label("in_progress_ticket"),
        func.sum(
            case(
                (Ticket.status == TicketStatus.QA, 1),
                else_=0,
            )
        ).label("qa_ticket"),
        func.sum(
            case(
                (Ticket.status == TicketStatus.DONE, 1),
                else_=0,
            )
        ).label("done_ticket"),
        func.sum(
            case(
                (Ticket.priority == TicketPriority.CRITICAL, 1),
                else_=0,
            )
        ).label("critical_priority_ticket"),
        func.sum(
            case(
                (Ticket.priority == TicketPriority.HIGH, 1),
                else_=0,
            )
        ).label("high_priority_ticket"),
        func.sum(
            case(
                (Ticket.priority == TicketPriority.MEDIUM, 1),
                else_=0,
            )
        ).label("medium_priority_ticket"),
        func.sum(
            case(
                (Ticket.priority == TicketPriority.LOW, 1),
                else_=0,
            )
        ).label("low_priority_ticket"),
    )

    query = query.filter(Ticket.is_deleted == False)

    if current_user.role.name == "USER":
        query = query.filter(Ticket.reporter_id == current_user.id)

    elif current_user.role.name == "STAFF_IT":
        query = query.filter(Ticket.pic_id == current_user.id)

    stats = query.first()

    return stats


def get_status_chart(
    db: Session,
    current_user: User,
):
    query = db.query(
        Ticket.status.label("status"),
        func.count(Ticket.id).label("count"),
    )

    query = query.filter(Ticket.is_deleted == False)

    if current_user.role.name == "USER":
        query = query.filter(Ticket.reporter_id == current_user.id)

    elif current_user.role.name == "STAFF_IT":
        query = query.filter(Ticket.pic_id == current_user.id)

    chart = (
        query
        .group_by(Ticket.status)
        .order_by(Ticket.status)
        .all()
    )

    return chart


def get_priority_chart(
    db: Session,
    current_user: User,
):
    query = db.query(
        Ticket.priority.label("priority"),
        func.count(Ticket.id).label("count"),
    )

    query = query.filter(Ticket.is_deleted == False)

    if current_user.role.name == "USER":
        query = query.filter(Ticket.reporter_id == current_user.id)

    elif current_user.role.name == "STAFF_IT":
        query = query.filter(Ticket.pic_id == current_user.id)

    chart = (
        query
        .group_by(Ticket.priority)
        .order_by(Ticket.priority)
        .all()
    )

    return chart