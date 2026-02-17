import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.company import Company


class FinancialData(SQLModel, table=True):
    __tablename__ = "financial_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companies.id")
    symbol: str = Field(max_length=20, index=True)
    record_date: Optional[datetime.date] = Field(default=None, index=True)

    # Price / valuation metrics
    ask: Optional[float] = None
    book_value: Optional[float] = None
    market_cap: Optional[float] = None

    # Earnings metrics
    ebitda: Optional[float] = None
    pe_ratio_ttm: Optional[float] = None
    pe_ratio_ftm: Optional[float] = None
    eps_estimate_qtr: Optional[float] = None
    eps_estimate_current_year: Optional[float] = None
    eps_estimate_next_year: Optional[float] = None
    eps_estimate_next_quarter: Optional[float] = None
    peg_ratio: Optional[float] = None

    # Calculated ratios
    garp_ratio: Optional[float] = None
    magic_formula_trailing: Optional[float] = None
    magic_formula_future: Optional[float] = None

    # Return metrics
    return_on_assets: Optional[float] = None
    return_on_equity: Optional[float] = None
    dividend_yield: Optional[float] = None

    # Income / balance sheet
    net_income: Optional[float] = None
    total_assets: Optional[float] = None

    # Price change metrics
    change_year_low_per: Optional[float] = None
    change_year_high_per: Optional[float] = None
    one_yr_target_price: Optional[float] = None

    # Rank columns
    rank_ebitda: Optional[int] = None
    rank_pe_ratio_ttm: Optional[int] = None
    rank_pe_ratio_ftm: Optional[int] = None
    rank_eps_estimate_qtr: Optional[int] = None
    rank_peg_ratio: Optional[int] = None
    rank_garp_ratio: Optional[int] = None
    rank_return_on_assets: Optional[int] = None
    rank_return_on_equity: Optional[int] = None
    rank_dividend_yield: Optional[int] = None
    rank_change_year_low_per: Optional[int] = None
    rank_change_year_high_per: Optional[int] = None
    rank_magic_formula_trailing: Optional[int] = None
    rank_magic_formula_future: Optional[int] = None

    company: Optional["Company"] = Relationship(back_populates="financials")
