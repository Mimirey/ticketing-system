from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse

router= APIRouter(
    prefix="/companies",
    tags=["Companies"]
)

@router.get("/", response_model=list[CompanyResponse])
def get_companies(db: Session = Depends(get_db)):
    return db.query(Company).all()
@router.post("/", response_model=CompanyResponse)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Company).filter(
        Company.name == data.name
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Company sudah ada"
        )
    company = Company(name=data.name)
    db.add(company)
    db.commit()
    db.refresh(company)

    return company