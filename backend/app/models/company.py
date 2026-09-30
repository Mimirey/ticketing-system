from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base

class Company(Base):
    __tablename__="companies"
    id= Column(Integer,primary_key=True, index= True)
    name= Column(String(100), unique=True, nullable=False)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    updated_at=Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    applications = relationship(
        "Application",
        back_populates="company",
        cascade="all, delete-orphan"
    )