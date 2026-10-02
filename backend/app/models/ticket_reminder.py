from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class TicketReminder(Base):
    __tablename__ = "ticket_reminders"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id"),
        nullable=False
    )
    reminder_type = Column(
        String(20),
        nullable=False
    )
    sent_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    ticket = relationship(
        "Ticket",
        backref="reminders"
    )
    __table_args__ = (
        UniqueConstraint(
            "ticket_id",
            "reminder_type",
            name="uq_ticket_reminder_type"
        ),
    )