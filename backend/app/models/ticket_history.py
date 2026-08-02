from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class TicketHistory(Base):
    __tablename__ = "ticket_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    changed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    field_changed = Column(String(50), nullable=False)
    old_value = Column(String(100), nullable=True)
    new_value = Column(String(100), nullable=False)

    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("Ticket", backref="history")
    changed_by = relationship("User")