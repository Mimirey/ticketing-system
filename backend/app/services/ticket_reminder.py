from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.ticket_reminder import TicketReminder
from app.models.enums import TicketStatus
from app.models.user import User
from app.services.telegram import send_telegram_message


REMINDER_24H = "24H"
REMINDER_1H = "1H"
REMINDER_OVERDUE = "OVERDUE"


def send_ticket_reminder(
    db: Session,
    ticket: Ticket,
    reminder_type: str,
):
    if ticket.status == TicketStatus.DONE:
        return False

    if not ticket.due_date:
        return False

    existing = (
        db.query(TicketReminder)
        .filter(
            TicketReminder.ticket_id == ticket.id,
            TicketReminder.reminder_type == reminder_type,
        )
        .first()
    )
    if existing:
        return False
    recipients = []

    if ticket.pic_id:
        pic = db.query(User).filter(User.id == ticket.pic_id).first()

        if pic and pic.telegram_chat_id:
            recipients.append(pic)
    pm_users = (
        db.query(User)
        .filter(
            User.role.has(name="PM_IT"),
            User.telegram_chat_id.isnot(None),
            User.is_active == True,
            User.is_deleted == False,
        )
        .all()
    )
    for user in pm_users:
        if user.id not in [u.id for u in recipients]:
            recipients.append(user)
    if not recipients:
        return False

    if reminder_type == REMINDER_24H:
        message = (
            f"REMINDER TICKET\n\n"
            f"Ticket: {ticket.ticket_number}\n"
            f"Judul: {ticket.title}\n"
            f"Status: {ticket.status.value}\n"
            f"Due date: {ticket.due_date}\n\n"
            f"Ticket akan jatuh tempo dalam kurang lebih 24 jam."
        )

    elif reminder_type == REMINDER_1H:
        message = (
            f"REMINDER TICKET\n\n"
            f"Ticket: {ticket.ticket_number}\n"
            f"Judul: {ticket.title}\n"
            f"Status: {ticket.status.value}\n"
            f"Due date: {ticket.due_date}\n\n"
            f"Ticket akan jatuh tempo dalam kurang lebih 1 jam."
        )
    elif reminder_type == REMINDER_OVERDUE:
        message = (
            f"TICKET OVERDUE\n\n"
            f"Ticket: {ticket.ticket_number}\n"
            f"Judul: {ticket.title}\n"
            f"Status: {ticket.status.value}\n"
            f"Due date: {ticket.due_date}\n\n"
            f"Ticket sudah melewati due date."
        )
    else:
        return False

    for user in recipients:
        send_telegram_message(
            user.telegram_chat_id,
            message,
        )

    reminder = TicketReminder(
        ticket_id=ticket.id,
        reminder_type=reminder_type,
    )
    db.add(reminder)
    db.commit()
    return True

def check_ticket_reminders(db: Session):
    now = datetime.now(timezone.utc)
    tickets = (
        db.query(Ticket)
        .filter(
            Ticket.due_date.isnot(None),
            Ticket.status != TicketStatus.DONE,
            Ticket.is_deleted == False,
        )
        .all()
    )
    for ticket in tickets:
        due_date = ticket.due_date
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        time_remaining = due_date - now
        if timedelta(hours=23) <= time_remaining <= timedelta(hours=25):
            send_ticket_reminder(
                db,
                ticket,
                REMINDER_24H,
            )
        elif timedelta(minutes=45) <= time_remaining <= timedelta(minutes=75):
            send_ticket_reminder(
                db,
                ticket,
                REMINDER_1H,
            )
        elif time_remaining.total_seconds() < 0:
            send_ticket_reminder(
                db,
                ticket,
                REMINDER_OVERDUE,
            )