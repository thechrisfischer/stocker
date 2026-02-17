from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_

from app.database import get_db
from app.models.user import User
from app.models.company import Company, CompanyRead
from app.services.auth import get_current_user

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("/", response_model=list[CompanyRead])
def list_companies(
    sector: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Company)

    if sector:
        statement = statement.where(Company.sector == sector)
    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(Company.symbol.ilike(pattern), Company.name.ilike(pattern))
        )

    statement = statement.order_by(Company.symbol).offset(skip).limit(limit)
    return db.exec(statement).all()


@router.get("/{symbol}", response_model=CompanyRead)
def get_company(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = db.exec(
        select(Company).where(Company.symbol == symbol.upper())
    ).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company
