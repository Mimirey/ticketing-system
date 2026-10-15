
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.activity_log_utils import log_activity
from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.application import Application
from app.models.company import Company
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
)

router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


@router.get("", response_model=list[ApplicationResponse])
def list_applications(
    company_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Application)

    if company_id is not None:
        query = query.filter(
            Application.companies.any(Company.id == company_id)
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
            detail="Application tidak ditemukan",
        )

    return application


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(
    data: ApplicationCreate,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    company_ids = list(dict.fromkeys(data.company_ids))

    if not company_ids:
        raise HTTPException(
            status_code=400,
            detail="Pilih minimal satu company",
        )

    companies = db.query(Company).filter(
        Company.id.in_(company_ids)
    ).all()

    if len(companies) != len(company_ids):
        raise HTTPException(
            status_code=404,
            detail="Satu atau lebih company tidak ditemukan",
        )

    existing = db.query(Application).filter(
        Application.name == data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Nama application sudah terdaftar",
        )

    application = Application(
        name=data.name,
        description=data.description,
        companies=companies,
    )

    db.add(application)
    db.flush()

    company_names = ", ".join(company.name for company in companies)

    log_activity(
        db,
        current_user.id,
        "CREATE_APPLICATION",
        f"{current_user.name} menambahkan aplikasi {application.name} "
        f"untuk company: {company_names}",
    )

    db.commit()
    db.refresh(application)

    return application


@router.put(
    "/{application_id}",
    response_model=ApplicationResponse,
)
def update_application(
    application_id: int,
    data: ApplicationUpdate,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application tidak ditemukan",
        )

    company_ids = list(dict.fromkeys(data.company_ids))

    if not company_ids:
        raise HTTPException(
            status_code=400,
            detail="Pilih minimal satu company",
        )

    companies = db.query(Company).filter(
        Company.id.in_(company_ids)
    ).all()

    if len(companies) != len(company_ids):
        raise HTTPException(
            status_code=404,
            detail="Satu atau lebih company tidak ditemukan",
        )

    existing = db.query(Application).filter(
        Application.name == data.name,
        Application.id != application_id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Nama application sudah terdaftar",
        )

    old_name = application.name

    application.name = data.name
    application.description = data.description
    application.companies = companies

    company_names = ", ".join(company.name for company in companies)

    log_activity(
        db,
        current_user.id,
        "UPDATE_APPLICATION",
        f"{current_user.name} mengubah aplikasi {old_name} "
        f"menjadi {application.name}; company: {company_names}",
    )

    db.commit()
    db.refresh(application)

    return application


@router.delete("/{application_id}")
def delete_application(
    application_id: int,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    application = db.query(Application).filter(
        Application.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application tidak ditemukan",
        )

    in_use = db.query(Ticket).filter(
        Ticket.application_id == application_id,
        Ticket.is_deleted.is_(False),
    ).count()

    if in_use:
        raise HTTPException(
            status_code=409,
            detail=f"Aplikasi masih dipakai oleh {in_use} ticket",
        )

    db.query(Ticket).filter(
        Ticket.application_id == application_id,
        Ticket.is_deleted.is_(True),
    ).update(
        {Ticket.application_id: None},
        synchronize_session=False,
    )

    app_name = application.name

    log_activity(
        db,
        current_user.id,
        "DELETE_APPLICATION",
        f"{current_user.name} menghapus aplikasi {app_name}",
    )

    db.delete(application)
    db.commit()

    return {"message": "Application berhasil dihapus"}
