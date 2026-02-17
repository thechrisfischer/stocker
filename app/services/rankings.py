"""
Stock ranking strategies ported from v1/calc_financials.py and v1/alg.py.

Each strategy returns a ranked list of companies based on financial metrics.
"""

from sqlmodel import Session, select, col

from app.models.company import Company
from app.models.financial_data import FinancialData

EXCLUDED_SECTORS = {"Finance", "Energy", "Miscellaneous"}

STRATEGIES = {
    "magic_formula_trailing": {
        "name": "Magic Formula (Trailing)",
        "description": "Ranks by PE ratio (TTM) + Return on Assets. Excludes Finance, Energy, Utilities, Miscellaneous sectors.",
    },
    "magic_formula_future": {
        "name": "Magic Formula (Future)",
        "description": "Ranks by PE ratio (FTM) + Return on Assets. Excludes Finance, Energy, Utilities, Miscellaneous sectors.",
    },
    "ebitda": {
        "name": "EBITDA",
        "description": "Ranks by Earnings Before Interest, Taxes, Depreciation, and Amortization (highest first).",
    },
    "pe_ratio_ttm": {
        "name": "PE Ratio (Trailing)",
        "description": "Ranks by trailing twelve-month Price-to-Earnings ratio (lowest first).",
    },
    "pe_ratio_ftm": {
        "name": "PE Ratio (Forward)",
        "description": "Ranks by forward twelve-month Price-to-Earnings ratio (lowest first).",
    },
    "garp_ratio": {
        "name": "GARP Ratio",
        "description": "Growth at a Reasonable Price — ranks by PE/PEG ratio (lowest first).",
    },
    "return_on_assets": {
        "name": "Return on Assets",
        "description": "Ranks by ROA (highest first).",
    },
    "return_on_equity": {
        "name": "Return on Equity",
        "description": "Ranks by ROE (highest first).",
    },
    "dividend_yield": {
        "name": "Dividend Yield",
        "description": "Ranks by dividend yield (highest first).",
    },
}


class RankingResult:
    """Lightweight container for ranking query results."""

    def __init__(self, symbol, name, rank, score, pe_ratio_ttm, pe_ratio_ftm,
                 garp_ratio, peg_ratio, return_on_assets):
        self.symbol = symbol
        self.name = name
        self.rank = rank
        self.score = score
        self.pe_ratio_ttm = pe_ratio_ttm
        self.pe_ratio_ftm = pe_ratio_ftm
        self.garp_ratio = garp_ratio
        self.peg_ratio = peg_ratio
        self.return_on_assets = return_on_assets


def get_rankings(db: Session, strategy: str, limit: int = 100) -> list[dict]:
    """Get ranked companies for a given strategy."""
    rank_col = f"rank_{strategy}"

    if not hasattr(FinancialData, rank_col):
        return []

    rank_attr = getattr(FinancialData, rank_col)
    score_attr = getattr(FinancialData, strategy, FinancialData.ebitda)

    statement = (
        select(
            Company.symbol,
            Company.name,
            rank_attr.label("rank"),
            score_attr.label("score"),
            FinancialData.pe_ratio_ttm,
            FinancialData.pe_ratio_ftm,
            FinancialData.garp_ratio,
            FinancialData.peg_ratio,
            FinancialData.return_on_assets,
        )
        .join(FinancialData, Company.id == FinancialData.company_id)
        .where(rank_attr.isnot(None), rank_attr > 0)
        .order_by(rank_attr.asc())
        .limit(limit)
    )

    rows = db.exec(statement).all()

    return [
        {
            "symbol": r.symbol,
            "name": r.name,
            "rank": r.rank,
            "score": r.score,
            "pe_ratio_ttm": r.pe_ratio_ttm,
            "pe_ratio_ftm": r.pe_ratio_ftm,
            "garp_ratio": r.garp_ratio,
            "peg_ratio": r.peg_ratio,
            "return_on_assets": r.return_on_assets,
        }
        for r in rows
    ]
