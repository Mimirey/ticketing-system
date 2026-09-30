from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.application import Application
from app.models.company import Company
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse
)

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


@router.get("/", response_model=list[ApplicationResponse])
def get_applications(
    company_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Application)

    if company_id:
        query = query.filter(
            Application.company_id == company_id
        )

    return query.all()


@router.post(
    "/",
    response_model=ApplicationResponse
)
def create_application(
    data: ApplicationCreate,
    db: Session = Depends(get_db)
):
    company = db.query(Company).filter(
        Company.id == data.company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company tidak ditemukan"
        )

    application = Application(
        company_id=data.company_id,
        name=data.name,
        description=data.description
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application