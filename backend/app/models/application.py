from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class Application(Base):
    __tablename__="applications"
    id= Column(Integer, primary_key=True, index=True)
    name= Column(String(100), nullable=False)
    description= Column(String(500), nullable=True)

    created_at=Column(DateTime(timezone=True), server_default=func.now())
    updated_at=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    companies = relationship(
        "Company",
        secondary="company_applications",
        back_populates="applications"
    )
    tickets= relationship(
        "Ticket",
        back_populates="application"
    )