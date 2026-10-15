from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy import UniqueConstraint

from app.db.database import Base


class CompanyApplication(Base):
    __tablename__ = "company_applications"
    __table_args__ = (
        UniqueConstraint(
            "company_id",
            "application_id",
            name="uq_company_application"
        ),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False
    )
    application_id = Column(
        Integer,
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False
    )