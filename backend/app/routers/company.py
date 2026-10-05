from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.db.database import get_db
from app.models.company import Company
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate

router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router.get("", response_model=list[CompanyResponse])
def list_companies(
    db: Session = Depends(get_db),
):
    return db.query(Company).order_by(Company.name).all()


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company tidak ditemukan"
        )

    return company


@router.post(
    "",
    response_model=CompanyResponse,
    status_code=201
)
def create_company(
    data: CompanyCreate,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    existing = db.query(Company).filter(
        Company.name == data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Company sudah terdaftar"
        )

    company = Company(
        name=data.name
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company


@router.put(
    "/{company_id}",
    response_model=CompanyResponse
)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company tidak ditemukan"
        )

    existing = db.query(Company).filter(
        Company.name == data.name,
        Company.id != company_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Nama company sudah digunakan"
        )

    company.name = data.name

    db.commit()
    db.refresh(company)

    return company


@router.delete("/{company_id}")
def delete_company(
    company_id: int,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        raise HTTPException(
            status_code=404,
            detail="Company tidak ditemukan"
        )

    in_use = db.query(Ticket).filter(
        Ticket.company_id == company_id,
        Ticket.is_deleted == False
    ).count()

    if in_use:
        raise HTTPException(
            status_code=409,
            detail=f"Company masih dipakai oleh {in_use} ticket"
        )

    db.query(Ticket).filter(
        Ticket.company_id == company_id,
        Ticket.is_deleted == True
    ).update(
        {
            Ticket.company_id: None,
            Ticket.application_id: None
        },
        synchronize_session=False
    )

    db.delete(company)
    db.commit()

    return {
        "message": "Company berhasil dihapus"
    }