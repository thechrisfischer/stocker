"""Stock ranking strategies ported from v1/alg.py and v1/data.py."""

import logging

from index import db
from .models import Company, FinancialData

logger = logging.getLogger(__name__)

EXCLUDED_SECTORS = ("Finance", "Energy", "Miscellaneous")


def _exclude_sectors(query):
    """Filter out sectors that distort ranking metrics."""
    query = query.filter(~Company.sector.in_(EXCLUDED_SECTORS))
    query = query.filter(~Company.sector.like("%Utilities%"))
    return query


def get_rankings(strategy):
    """Get ranked companies for a given strategy.

    Supported strategies:
        magic_formula_trailing, magic_formula_future, ebitda,
        pe_ratio_ttm, pe_ratio_ftm, garp_ratio,
        return_on_assets, return_on_equity, dividend_yield
    """
    rank_col = "rank_" + strategy
    score_col = strategy

    if not hasattr(FinancialData, rank_col) or not hasattr(FinancialData, score_col):
        return []

    query = (
        db.session.query(
            Company.id,
            Company.symbol,
            Company.name,
            getattr(FinancialData, score_col).label("score"),
            getattr(FinancialData, rank_col).label("rank"),
            FinancialData.pe_ratio_ttm,
            FinancialData.pe_ratio_ftm,
            FinancialData.peg_ratio,
            FinancialData.garp_ratio,
            FinancialData.return_on_assets,
        )
        .join(FinancialData, Company.id == FinancialData.company_id)
        .filter(getattr(FinancialData, rank_col) > 0)
        .order_by(getattr(FinancialData, rank_col).asc())
    )

    results = []
    for row in query.all():
        results.append({
            "id": row.id,
            "symbol": row.symbol,
            "name": row.name,
            "score": row.score,
            "rank": row.rank,
            "pe_ratio_ttm": row.pe_ratio_ttm,
            "pe_ratio_ftm": row.pe_ratio_ftm,
            "peg_ratio": row.peg_ratio,
            "garp_ratio": row.garp_ratio,
            "return_on_assets": row.return_on_assets,
        })

    return results


def get_magic_formula_trailing():
    """Magic Formula = rank_pe_ratio_ttm + rank_return_on_assets (lower is better)."""
    query = (
        db.session.query(
            Company.symbol,
            (FinancialData.rank_pe_ratio_ttm + FinancialData.rank_return_on_assets).label("score"),
        )
        .join(FinancialData, Company.id == FinancialData.company_id)
        .filter(FinancialData.rank_pe_ratio_ttm.isnot(None))
        .filter(FinancialData.rank_return_on_assets.isnot(None))
    )
    query = _exclude_sectors(query)
    query = query.order_by("score")

    return [{"symbol": r.symbol, "score": r.score} for r in query.all()]


def get_magic_formula_future():
    """Magic Formula Future = rank_pe_ratio_ftm + rank_return_on_assets."""
    query = (
        db.session.query(
            Company.symbol,
            (FinancialData.rank_pe_ratio_ftm + FinancialData.rank_return_on_assets).label("score"),
        )
        .join(FinancialData, Company.id == FinancialData.company_id)
        .filter(FinancialData.rank_pe_ratio_ftm.isnot(None))
        .filter(FinancialData.rank_return_on_assets.isnot(None))
    )
    query = _exclude_sectors(query)
    query = query.order_by("score")

    return [{"symbol": r.symbol, "score": r.score} for r in query.all()]


def get_garp():
    """Growth at a Reasonable Price (GARP) - sorted by garp_ratio ascending."""
    query = (
        db.session.query(
            Company.symbol,
            FinancialData.garp_ratio.label("score"),
        )
        .join(FinancialData, Company.id == FinancialData.company_id)
        .filter(FinancialData.garp_ratio > 0)
    )
    query = _exclude_sectors(query)
    query = query.order_by(FinancialData.garp_ratio.asc())

    return [{"symbol": r.symbol, "score": r.score} for r in query.all()]


VALID_STRATEGIES = [
    "magic_formula_trailing",
    "magic_formula_future",
    "ebitda",
    "pe_ratio_ttm",
    "pe_ratio_ftm",
    "garp_ratio",
    "return_on_assets",
    "return_on_equity",
    "dividend_yield",
]
