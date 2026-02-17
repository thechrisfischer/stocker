from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.financial_data import FinancialData


class CompanyBase(SQLModel):
    symbol: str = Field(max_length=20, unique=True, index=True)
    name: Optional[str] = Field(default=None, max_length=255)
    sector: Optional[str] = Field(default=None, max_length=100)
    industry: Optional[str] = Field(default=None, max_length=100)


class Company(CompanyBase, table=True):
    __tablename__ = "companies"

    id: Optional[int] = Field(default=None, primary_key=True)
    financials: list["FinancialData"] = Relationship(back_populates="company")


class CompanyRead(CompanyBase):
    id: int
