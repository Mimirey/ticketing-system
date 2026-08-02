from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.db.database import Base
from app.models.enums import TicketType, TicketPriority, TicketStatus

class Ticket(Base):
    __tablename__="tickets"
    id= Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(20), unique=True, index=True, nullable=True)

    type = Column(SQLEnum(TicketType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(SQLEnum(TicketPriority), nullable=False, default=TicketPriority.LOW)
    status = Column(SQLEnum(TicketStatus), nullable=False, default=TicketStatus.OPEN)
    module = Column(String(100), nullable=True)

    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pic_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    is_deleted = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reporter = relationship("User", foreign_keys=[reporter_id], backref="tickets_reported")
    pic = relationship("User", foreign_keys=[pic_id], backref="tickets_assigned")