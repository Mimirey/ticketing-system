from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class Notification(Base):
    __tablename__= "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ticket_id= Column(Integer, ForeignKey("tickets.id"), nullable=True)
    title= Column(String(200), nullable=False)
    message= Column(String(500), nullable=False)
    is_read= Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users= relationship("User")
    ticket= relationship("Ticket")