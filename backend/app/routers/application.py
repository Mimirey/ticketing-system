from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.application import Application
from app.models.company import Company
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse
)

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    company_id: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Application)

    if company_id is not None:
        query = query.filter(
            Application.company_id == company_id
        )

    return query.order_by(Application.name).all()


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application tidak ditemukan"
        )

    return application


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=201
)
def create_application(
    data: ApplicationCreate,
    current_user: User = Depends(
        require_role("PM_IT")
    ),
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

    existing = db.query(Application).filter(
        Application.company_id == data.company_id,
        Application.name == data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Application sudah terdaftar pada company tersebut"
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


@router.put(
    "/{application_id}",
    response_model=ApplicationResponse
)
def update_application(
    application_id: int,
    data: ApplicationUpdate,
    current_user: User = Depends(
        require_role("PM_IT")
    ),
    db: Session = Depends(get_db)
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application tidak ditemukan"
        )

    company = db.query(Company).filter(
        Company.id == data.company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company tidak ditemukan"
        )

    existing = db.query(Application).filter(
        Application.company_id == data.company_id,
        Application.name == data.name,
        Application.id != application_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Application sudah terdaftar pada company tersebut"
        )

    application.company_id = data.company_id
    application.name = data.name
    application.description = data.description

    db.commit()
    db.refresh(application)

    return application


@router.delete("/{application_id}")
def delete_application(
    application_id: int,
    current_user: User = Depends(
        require_role("PM_IT")
    ),
    db: Session = Depends(get_db),
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application tidak ditemukan"
        )

    in_use = db.query(Ticket).filter(
        Ticket.application_id == application_id,
        Ticket.is_deleted == False
    ).count()

    if in_use:
        raise HTTPException(
            status_code=409,
            detail=f"Aplikasi masih dipakai oleh {in_use} ticket"
        )

    db.query(Ticket).filter(
        Ticket.application_id == application_id,
        Ticket.is_deleted == True
    ).update(
        {
            Ticket.application_id: None
        },
        synchronize_session=False
    )

    db.delete(application)
    db.commit()