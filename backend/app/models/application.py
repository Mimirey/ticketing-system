from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class Application(Base):
    __tablename__="applications"
    id= Column(Integer, primary_key=True, index=True)
    company_id=Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
    )
    name= Column(String(100), nullable=False)
    description= Column(String(500), nullable=True)

    created_at=Column(DateTime(timezone=True), server_default=func.now())
    updated_at=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    company= relationship(
        "Company",
        back_populates="applications"
    )
    tickets= relationship(
        "Ticket",
        back_populates="application"
    )