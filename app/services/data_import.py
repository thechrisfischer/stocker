"""
Stock data import service using yfinance.

Fetches financial metrics for publicly traded companies and populates
the database with current data and computed rankings.
"""

import datetime
import logging
from typing import Optional

import yfinance as yf
from sqlmodel import Session, select

from app.models.company import Company
from app.models.financial_data import FinancialData

logger = logging.getLogger(__name__)

# S&P 500 representative sample + popular large/mid caps
# Full list would come from a proper source; this seeds enough for a working demo
SEED_SYMBOLS = [
    # Tech
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSM", "AVGO", "ORCL", "CRM",
    "ADBE", "AMD", "INTC", "CSCO", "TXN", "QCOM", "IBM", "NOW", "INTU", "AMAT",
    "MU", "LRCX", "KLAC", "SNPS", "CDNS", "MRVL", "FTNT", "PANW", "CRWD", "ZS",
    # Healthcare
    "UNH", "JNJ", "LLY", "ABBV", "MRK", "PFE", "TMO", "ABT", "DHR", "BMY",
    "AMGN", "GILD", "ISRG", "VRTX", "REGN", "MDT", "SYK", "BSX", "EW", "ZTS",
    # Financials
    "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "SPGI", "BLK",
    "C", "AXP", "SCHW", "CB", "MMC", "PGR", "ICE", "CME", "AON", "MET",
    # Consumer
    "WMT", "PG", "KO", "PEP", "COST", "MCD", "NKE", "SBUX", "TGT", "EL",
    "CL", "MDLZ", "GIS", "KHC", "HSY", "K", "SJM", "CPB", "HRL", "MKC",
    # Industrials
    "CAT", "DE", "UNP", "HON", "RTX", "BA", "LMT", "GD", "GE", "MMM",
    "UPS", "FDX", "WM", "RSG", "EMR", "ITW", "ETN", "PH", "ROK", "SWK",
    # Energy
    "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "PSX", "VLO", "OXY", "DVN",
    # Materials
    "LIN", "APD", "ECL", "SHW", "DD", "NEM", "FCX", "NUE", "VMC", "MLM",
    # Real Estate
    "PLD", "AMT", "EQIX", "CCI", "PSA", "O", "SPG", "DLR", "WELL", "AVB",
    # Utilities
    "NEE", "DUK", "SO", "D", "AEP", "SRE", "EXC", "XEL", "WEC", "ES",
    # Communication
    "GOOG", "DIS", "CMCSA", "NFLX", "T", "VZ", "TMUS", "CHTR", "EA", "TTWO",
]

EXCLUDED_SECTORS = {"Financial Services", "Energy", "Utilities"}


def fetch_and_store(db: Session, symbols: Optional[list[str]] = None) -> dict:
    """Fetch financial data for symbols and store in the database.

    Returns a summary dict with counts of companies processed, succeeded, failed.
    """
    if symbols is None:
        symbols = SEED_SYMBOLS

    # De-duplicate
    symbols = list(dict.fromkeys(symbols))

    stats = {"total": len(symbols), "succeeded": 0, "failed": 0, "skipped": 0}
    today = datetime.date.today()

    for i, symbol in enumerate(symbols):
        try:
            logger.info(f"[{i+1}/{len(symbols)}] Fetching {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info

            if not info or info.get("regularMarketPrice") is None:
                logger.warning(f"  No data for {symbol}, skipping")
                stats["skipped"] += 1
                continue

            # Upsert company
            company = db.exec(
                select(Company).where(Company.symbol == symbol)
            ).first()
            if not company:
                company = Company(
                    symbol=symbol,
                    name=info.get("shortName") or info.get("longName"),
                    sector=info.get("sector"),
                    industry=info.get("industry"),
                )
                db.add(company)
                db.commit()
                db.refresh(company)
            else:
                company.name = info.get("shortName") or info.get("longName") or company.name
                company.sector = info.get("sector") or company.sector
                company.industry = info.get("industry") or company.industry
                db.add(company)
                db.commit()
                db.refresh(company)

            # Extract metrics
            ask = info.get("currentPrice") or info.get("regularMarketPrice")
            book_value = info.get("bookValue")
            market_cap = info.get("marketCap")
            ebitda = info.get("ebitda")
            pe_ratio_ttm = info.get("trailingPE")
            pe_ratio_ftm = info.get("forwardPE")
            eps_current_year = info.get("epsCurrentYear")
            eps_next_year = info.get("epsForward")
            peg_ratio = info.get("pegRatio")
            return_on_assets = info.get("returnOnAssets")
            return_on_equity = info.get("returnOnEquity")
            dividend_yield = info.get("dividendYield")
            net_income = info.get("netIncomeToCommon")
            total_assets = info.get("totalAssets")

            # Calculate derived metrics
            garp_ratio = None
            if pe_ratio_ttm and peg_ratio and peg_ratio > 0:
                garp_ratio = pe_ratio_ttm / peg_ratio

            magic_formula_trailing = None  # Calculated during ranking
            magic_formula_future = None

            # Convert percentages (yfinance returns decimals like 0.15 for 15%)
            if return_on_assets is not None:
                return_on_assets = round(return_on_assets * 100, 2)
            if return_on_equity is not None:
                return_on_equity = round(return_on_equity * 100, 2)
            if dividend_yield is not None:
                dividend_yield = round(dividend_yield * 100, 2)

            # Check for existing record for today
            existing = db.exec(
                select(FinancialData).where(
                    FinancialData.company_id == company.id,
                    FinancialData.record_date == today,
                )
            ).first()

            if existing:
                # Update existing record
                fd = existing
            else:
                fd = FinancialData(company_id=company.id, symbol=symbol, record_date=today)

            fd.ask = ask
            fd.book_value = book_value
            fd.market_cap = market_cap
            fd.ebitda = ebitda
            fd.pe_ratio_ttm = pe_ratio_ttm
            fd.pe_ratio_ftm = pe_ratio_ftm
            fd.eps_estimate_current_year = eps_current_year
            fd.eps_estimate_next_year = eps_next_year
            fd.peg_ratio = peg_ratio
            fd.garp_ratio = garp_ratio
            fd.return_on_assets = return_on_assets
            fd.return_on_equity = return_on_equity
            fd.dividend_yield = dividend_yield
            fd.net_income = net_income
            fd.total_assets = total_assets

            db.add(fd)
            db.commit()
            stats["succeeded"] += 1

        except Exception as e:
            logger.error(f"  Error fetching {symbol}: {e}")
            stats["failed"] += 1
            db.rollback()

    return stats


def compute_rankings(db: Session) -> int:
    """Compute rank columns for all financial data records.

    Returns the number of records ranked.
    """
    # Get the latest record_date
    from sqlalchemy import func
    latest_date = db.exec(
        select(func.max(FinancialData.record_date))
    ).first()

    if not latest_date:
        return 0

    # Get all records for the latest date, joined with company for sector filtering
    records = db.exec(
        select(FinancialData, Company)
        .join(Company, FinancialData.company_id == Company.id)
        .where(FinancialData.record_date == latest_date)
    ).all()

    if not records:
        return 0

    # Ranking definitions: (metric_attr, rank_attr, ascending, sector_filter)
    # ascending=True means lower values get lower (better) rank
    rank_configs = [
        ("ebitda", "rank_ebitda", False, None),
        ("pe_ratio_ttm", "rank_pe_ratio_ttm", True, None),
        ("pe_ratio_ftm", "rank_pe_ratio_ftm", True, None),
        ("peg_ratio", "rank_peg_ratio", True, None),
        ("garp_ratio", "rank_garp_ratio", True, None),
        ("return_on_assets", "rank_return_on_assets", False, None),
        ("return_on_equity", "rank_return_on_equity", False, None),
        ("dividend_yield", "rank_dividend_yield", False, None),
    ]

    for metric_attr, rank_attr, ascending, _ in rank_configs:
        # Collect (fd, value) pairs where value is not None and positive for ratios
        scored = []
        for fd, company in records:
            val = getattr(fd, metric_attr)
            if val is not None and val > 0:
                scored.append((fd, val))

        # Sort
        scored.sort(key=lambda x: x[1], reverse=not ascending)

        # Assign ranks
        for rank, (fd, _) in enumerate(scored, 1):
            setattr(fd, rank_attr, rank)
            db.add(fd)

    # Magic Formula rankings (composite of PE rank + ROA rank)
    # Exclude Finance, Energy, Utilities sectors
    for fd, company in records:
        if company.sector in EXCLUDED_SECTORS:
            fd.rank_magic_formula_trailing = None
            fd.rank_magic_formula_future = None
            db.add(fd)
            continue

        if fd.rank_pe_ratio_ttm and fd.rank_return_on_assets:
            fd.magic_formula_trailing = fd.rank_pe_ratio_ttm + fd.rank_return_on_assets
        if fd.rank_pe_ratio_ftm and fd.rank_return_on_assets:
            fd.magic_formula_future = fd.rank_pe_ratio_ftm + fd.rank_return_on_assets

        db.add(fd)

    # Now rank the magic formula composite scores
    for mf_attr, mf_rank_attr in [
        ("magic_formula_trailing", "rank_magic_formula_trailing"),
        ("magic_formula_future", "rank_magic_formula_future"),
    ]:
        scored = []
        for fd, company in records:
            if company.sector in EXCLUDED_SECTORS:
                continue
            val = getattr(fd, mf_attr)
            if val is not None and val > 0:
                scored.append((fd, val))

        scored.sort(key=lambda x: x[1])  # Lower composite score = better
        for rank, (fd, _) in enumerate(scored, 1):
            setattr(fd, mf_rank_attr, rank)
            db.add(fd)

    db.commit()
    return len(records)
