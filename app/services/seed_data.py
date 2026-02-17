"""
Seed data for StockRocker.

Contains real financial data for ~100 major companies to bootstrap the database
when yfinance API isn't available (rate limits, sandbox environments, etc).

Data sourced from public financial statements and market data (approximate values).
Run the full yfinance import for up-to-date numbers.
"""

import datetime
from sqlmodel import Session, select

from app.models.company import Company
from app.models.financial_data import FinancialData

# Approximate financial data for major US stocks (as of early 2026)
# Format: (symbol, name, sector, industry, ask, market_cap, ebitda,
#          pe_ttm, pe_ftm, peg, roa%, roe%, div_yield%, book_value)
SEED_COMPANIES = [
    # Tech
    ("AAPL", "Apple Inc.", "Technology", "Consumer Electronics", 232.0, 3520e9, 134e9, 38.5, 33.2, 2.1, 30.5, 160.0, 0.44, 4.38),
    ("MSFT", "Microsoft Corp.", "Technology", "Software—Infrastructure", 420.0, 3120e9, 125e9, 35.8, 30.5, 2.3, 21.5, 38.0, 0.72, 36.12),
    ("GOOGL", "Alphabet Inc.", "Communication Services", "Internet Content & Information", 175.0, 2150e9, 112e9, 23.5, 20.8, 1.1, 16.2, 30.5, 0.45, 24.50),
    ("AMZN", "Amazon.com Inc.", "Consumer Cyclical", "Internet Retail", 215.0, 2200e9, 92e9, 42.0, 32.5, 1.8, 8.5, 22.5, 0.0, 22.10),
    ("META", "Meta Platforms Inc.", "Communication Services", "Internet Content & Information", 580.0, 1480e9, 72e9, 26.2, 22.0, 1.0, 18.5, 35.0, 0.35, 64.50),
    ("NVDA", "NVIDIA Corp.", "Technology", "Semiconductors", 130.0, 3200e9, 78e9, 55.0, 32.0, 1.2, 55.0, 120.0, 0.03, 2.74),
    ("TSM", "Taiwan Semiconductor", "Technology", "Semiconductors", 195.0, 1010e9, 45e9, 28.0, 22.5, 1.3, 15.0, 28.0, 1.25, 18.40),
    ("AVGO", "Broadcom Inc.", "Technology", "Semiconductors", 220.0, 1020e9, 22e9, 95.0, 30.0, 1.6, 10.2, 25.0, 1.15, 12.30),
    ("ORCL", "Oracle Corp.", "Technology", "Software—Infrastructure", 175.0, 485e9, 22e9, 38.0, 26.0, 1.7, 12.0, 85.0, 0.95, 3.10),
    ("CRM", "Salesforce Inc.", "Technology", "Software—Application", 310.0, 298e9, 14e9, 48.0, 28.0, 1.5, 7.0, 10.5, 0.55, 62.40),
    ("ADBE", "Adobe Inc.", "Technology", "Software—Application", 445.0, 195e9, 9.5e9, 35.0, 26.0, 1.8, 18.0, 36.0, 0.0, 28.50),
    ("AMD", "Advanced Micro Devices", "Technology", "Semiconductors", 120.0, 194e9, 6.5e9, 45.0, 28.0, 0.9, 3.5, 4.8, 0.0, 41.20),
    ("INTC", "Intel Corp.", "Technology", "Semiconductors", 22.0, 95e9, 5.0e9, 0.0, 25.0, 3.5, -1.5, -3.0, 0.0, 24.50),
    ("CSCO", "Cisco Systems Inc.", "Technology", "Communication Equipment", 58.0, 232e9, 17e9, 24.0, 15.0, 2.5, 10.5, 28.0, 2.75, 11.20),
    ("TXN", "Texas Instruments", "Technology", "Semiconductors", 180.0, 163e9, 8.5e9, 32.0, 28.0, 3.8, 15.0, 42.0, 2.85, 8.90),
    ("QCOM", "Qualcomm Inc.", "Technology", "Semiconductors", 165.0, 183e9, 12e9, 16.5, 14.0, 1.2, 18.0, 42.0, 1.95, 15.70),
    ("IBM", "International Business Machines", "Technology", "IT Services", 240.0, 220e9, 15e9, 28.0, 20.0, 2.0, 6.5, 30.0, 2.75, 26.80),
    ("NOW", "ServiceNow Inc.", "Technology", "Software—Application", 920.0, 190e9, 5.0e9, 115.0, 55.0, 2.2, 6.0, 18.0, 0.0, 42.50),
    ("INTU", "Intuit Inc.", "Technology", "Software—Application", 620.0, 173e9, 6.0e9, 55.0, 32.0, 2.0, 12.0, 18.0, 0.62, 46.80),
    ("AMAT", "Applied Materials", "Technology", "Semiconductor Equipment", 175.0, 142e9, 9.5e9, 20.0, 18.0, 1.5, 20.0, 48.0, 0.80, 18.20),
    # Healthcare
    ("UNH", "UnitedHealth Group", "Healthcare", "Healthcare Plans", 520.0, 475e9, 30e9, 18.0, 16.0, 1.5, 8.5, 25.0, 1.45, 88.50),
    ("JNJ", "Johnson & Johnson", "Healthcare", "Drug Manufacturers", 152.0, 365e9, 28e9, 22.0, 15.0, 2.8, 8.0, 20.0, 3.25, 28.40),
    ("LLY", "Eli Lilly & Co.", "Healthcare", "Drug Manufacturers", 800.0, 760e9, 12e9, 85.0, 38.0, 1.5, 15.0, 55.0, 0.65, 18.50),
    ("ABBV", "AbbVie Inc.", "Healthcare", "Drug Manufacturers", 180.0, 318e9, 22e9, 55.0, 16.0, 1.8, 6.0, 45.0, 3.55, 5.20),
    ("MRK", "Merck & Co.", "Healthcare", "Drug Manufacturers", 100.0, 252e9, 18e9, 16.0, 12.0, 1.5, 12.0, 35.0, 2.85, 12.80),
    ("PFE", "Pfizer Inc.", "Healthcare", "Drug Manufacturers", 26.0, 147e9, 12e9, 18.0, 10.5, 1.5, 3.5, 8.0, 6.50, 12.50),
    ("TMO", "Thermo Fisher Scientific", "Healthcare", "Diagnostics & Research", 555.0, 208e9, 12e9, 28.0, 22.0, 2.0, 5.5, 14.0, 0.22, 72.50),
    ("ABT", "Abbott Laboratories", "Healthcare", "Medical Devices", 115.0, 198e9, 10e9, 22.5, 20.0, 2.5, 7.0, 16.0, 1.80, 21.30),
    ("AMGN", "Amgen Inc.", "Healthcare", "Drug Manufacturers", 295.0, 158e9, 13e9, 22.0, 14.5, 2.0, 8.0, 60.0, 3.25, 8.20),
    ("GILD", "Gilead Sciences", "Healthcare", "Drug Manufacturers", 95.0, 117e9, 11e9, 12.0, 11.0, 1.8, 10.0, 28.0, 3.40, 22.80),
    # Financials
    ("JPM", "JPMorgan Chase", "Financial Services", "Banks", 245.0, 700e9, 0.0, 13.0, 12.0, 1.5, 1.2, 16.0, 2.00, 110.50),
    ("V", "Visa Inc.", "Financial Services", "Credit Services", 310.0, 580e9, 22e9, 32.0, 28.0, 1.8, 18.0, 48.0, 0.72, 20.40),
    ("MA", "Mastercard Inc.", "Financial Services", "Credit Services", 520.0, 470e9, 15e9, 36.0, 30.0, 1.9, 25.0, 170.0, 0.55, 8.50),
    ("BAC", "Bank of America", "Financial Services", "Banks", 44.0, 340e9, 0.0, 14.0, 12.0, 1.2, 0.9, 10.0, 2.30, 34.80),
    ("WFC", "Wells Fargo", "Financial Services", "Banks", 72.0, 240e9, 0.0, 14.5, 12.5, 1.3, 1.0, 12.0, 2.20, 48.50),
    ("GS", "Goldman Sachs", "Financial Services", "Capital Markets", 580.0, 180e9, 0.0, 15.0, 13.0, 0.9, 1.0, 12.0, 2.10, 325.00),
    ("SPGI", "S&P Global", "Financial Services", "Financial Data", 480.0, 148e9, 6.8e9, 42.0, 30.0, 2.2, 10.0, 25.0, 0.72, 50.40),
    ("BLK", "BlackRock Inc.", "Financial Services", "Asset Management", 950.0, 140e9, 7.5e9, 24.0, 22.0, 1.8, 3.5, 15.0, 2.15, 255.00),
    ("AXP", "American Express", "Financial Services", "Credit Services", 285.0, 200e9, 0.0, 20.0, 17.0, 1.3, 3.5, 32.0, 1.00, 32.80),
    ("PGR", "Progressive Corp.", "Financial Services", "Insurance", 250.0, 145e9, 0.0, 18.0, 16.0, 1.5, 10.0, 35.0, 0.25, 35.20),
    # Consumer Staples
    ("WMT", "Walmart Inc.", "Consumer Defensive", "Discount Stores", 90.0, 720e9, 35e9, 38.0, 30.0, 3.5, 7.0, 20.0, 0.95, 22.80),
    ("PG", "Procter & Gamble", "Consumer Defensive", "Household Products", 165.0, 390e9, 22e9, 28.0, 24.0, 3.5, 12.0, 30.0, 2.35, 18.50),
    ("KO", "Coca-Cola Co.", "Consumer Defensive", "Beverages", 62.0, 265e9, 15e9, 25.0, 22.0, 3.0, 10.0, 40.0, 2.80, 6.20),
    ("PEP", "PepsiCo Inc.", "Consumer Defensive", "Beverages", 148.0, 202e9, 16e9, 22.0, 20.0, 2.8, 9.5, 50.0, 3.45, 14.80),
    ("COST", "Costco Wholesale", "Consumer Defensive", "Discount Stores", 920.0, 405e9, 12e9, 52.0, 45.0, 4.5, 12.0, 30.0, 0.50, 55.20),
    ("MCD", "McDonald's Corp.", "Consumer Cyclical", "Restaurants", 290.0, 210e9, 14e9, 25.0, 23.0, 2.5, 15.0, 0.0, 2.25, -8.50),
    ("NKE", "Nike Inc.", "Consumer Cyclical", "Footwear & Accessories", 72.0, 107e9, 6.5e9, 28.0, 25.0, 2.2, 12.0, 35.0, 1.80, 10.50),
    ("SBUX", "Starbucks Corp.", "Consumer Cyclical", "Restaurants", 108.0, 120e9, 7.5e9, 32.0, 28.0, 2.0, 14.0, 0.0, 2.10, -8.20),
    ("CL", "Colgate-Palmolive", "Consumer Defensive", "Household Products", 92.0, 75e9, 5.2e9, 28.0, 24.0, 3.2, 20.0, 200.0, 2.15, 2.80),
    ("MDLZ", "Mondelez International", "Consumer Defensive", "Confectioners", 68.0, 90e9, 7.8e9, 22.0, 20.0, 2.5, 6.0, 16.0, 2.55, 18.20),
    # Industrials
    ("CAT", "Caterpillar Inc.", "Industrials", "Farm & Heavy Construction", 350.0, 168e9, 16e9, 16.0, 16.5, 1.8, 12.0, 55.0, 1.55, 28.50),
    ("DE", "Deere & Company", "Industrials", "Farm & Heavy Construction", 440.0, 122e9, 14e9, 15.5, 18.0, 2.0, 10.0, 35.0, 1.35, 45.20),
    ("HON", "Honeywell International", "Industrials", "Diversified Industrials", 210.0, 137e9, 10e9, 22.0, 20.0, 2.2, 8.0, 30.0, 2.00, 25.80),
    ("UNP", "Union Pacific Corp.", "Industrials", "Railroads", 230.0, 140e9, 12e9, 22.0, 20.0, 2.5, 10.0, 42.0, 2.10, 22.50),
    ("RTX", "RTX Corp.", "Industrials", "Aerospace & Defense", 125.0, 165e9, 12e9, 35.0, 22.0, 1.8, 3.5, 8.0, 2.10, 55.20),
    ("BA", "Boeing Co.", "Industrials", "Aerospace & Defense", 175.0, 130e9, 0.0, 0.0, 0.0, 0.0, -5.0, 0.0, 0.0, -25.40),
    ("GE", "GE Aerospace", "Industrials", "Aerospace & Defense", 190.0, 205e9, 8.5e9, 35.0, 28.0, 1.5, 5.0, 22.0, 0.65, 18.50),
    ("UPS", "United Parcel Service", "Industrials", "Integrated Freight", 120.0, 100e9, 12e9, 18.0, 16.0, 2.0, 12.0, 30.0, 4.80, 12.30),
    ("WM", "Waste Management", "Industrials", "Waste Management", 215.0, 85e9, 7.5e9, 32.0, 28.0, 2.5, 8.0, 30.0, 1.35, 14.80),
    ("EMR", "Emerson Electric", "Industrials", "Diversified Industrials", 120.0, 68e9, 5.5e9, 30.0, 22.0, 2.0, 5.0, 12.0, 1.75, 35.20),
    # Energy
    ("XOM", "Exxon Mobil Corp.", "Energy", "Oil & Gas", 108.0, 472e9, 65e9, 14.0, 13.0, 2.5, 10.0, 18.0, 3.35, 48.50),
    ("CVX", "Chevron Corp.", "Energy", "Oil & Gas", 152.0, 275e9, 45e9, 14.5, 13.5, 2.8, 8.0, 14.0, 4.20, 88.50),
    ("COP", "ConocoPhillips", "Energy", "Oil & Gas", 100.0, 128e9, 22e9, 12.0, 11.5, 1.5, 8.5, 18.0, 2.85, 38.20),
    ("SLB", "Schlumberger NV", "Energy", "Oil & Gas Equipment", 42.0, 60e9, 8.5e9, 14.0, 12.5, 0.8, 8.0, 22.0, 2.50, 14.50),
    ("EOG", "EOG Resources", "Energy", "Oil & Gas", 125.0, 72e9, 10e9, 10.0, 10.5, 0.9, 12.0, 22.0, 2.80, 42.50),
    # Materials
    ("LIN", "Linde PLC", "Basic Materials", "Specialty Chemicals", 440.0, 210e9, 12e9, 32.0, 28.0, 2.5, 6.0, 15.0, 1.20, 85.00),
    ("SHW", "Sherwin-Williams", "Basic Materials", "Specialty Chemicals", 340.0, 85e9, 4.5e9, 35.0, 28.0, 2.8, 12.0, 60.0, 0.82, 8.50),
    ("APD", "Air Products & Chemicals", "Basic Materials", "Specialty Chemicals", 280.0, 62e9, 5.0e9, 22.0, 20.0, 2.0, 8.0, 16.0, 2.40, 55.20),
    ("FCX", "Freeport-McMoRan", "Basic Materials", "Copper", 42.0, 60e9, 8.5e9, 22.0, 18.0, 0.8, 8.0, 22.0, 1.45, 16.80),
    ("NUE", "Nucor Corp.", "Basic Materials", "Steel", 135.0, 32e9, 5.5e9, 12.0, 14.0, 1.2, 10.0, 18.0, 1.35, 62.50),
    # Utilities
    ("NEE", "NextEra Energy", "Utilities", "Utilities—Regulated Electric", 75.0, 152e9, 12e9, 22.0, 20.0, 2.5, 3.5, 10.0, 2.75, 22.50),
    ("DUK", "Duke Energy", "Utilities", "Utilities—Regulated Electric", 108.0, 83e9, 12e9, 18.0, 17.0, 3.0, 2.5, 8.0, 3.65, 62.50),
    ("SO", "Southern Co.", "Utilities", "Utilities—Regulated Electric", 85.0, 92e9, 10e9, 20.0, 18.0, 2.8, 3.0, 12.0, 3.25, 28.50),
    # Communication
    ("DIS", "Walt Disney Co.", "Communication Services", "Entertainment", 110.0, 200e9, 14e9, 38.0, 22.0, 1.5, 4.5, 8.0, 0.82, 52.80),
    ("NFLX", "Netflix Inc.", "Communication Services", "Entertainment", 1000.0, 430e9, 10e9, 48.0, 35.0, 1.5, 15.0, 32.0, 0.0, 25.80),
    ("CMCSA", "Comcast Corp.", "Communication Services", "Telecom", 35.0, 138e9, 28e9, 10.0, 9.5, 1.0, 5.0, 14.0, 3.25, 18.20),
    ("T", "AT&T Inc.", "Communication Services", "Telecom", 25.0, 178e9, 42e9, 16.0, 10.0, 2.5, 4.0, 12.0, 4.05, 12.50),
    ("VZ", "Verizon Communications", "Communication Services", "Telecom", 42.0, 177e9, 48e9, 10.0, 9.0, 2.5, 5.0, 18.0, 6.20, 22.80),
    # Consumer Cyclical
    ("HD", "Home Depot Inc.", "Consumer Cyclical", "Home Improvement Retail", 380.0, 378e9, 24e9, 25.0, 23.0, 2.0, 30.0, 0.0, 2.35, -2.50),
    ("LOW", "Lowe's Companies", "Consumer Cyclical", "Home Improvement Retail", 250.0, 142e9, 14e9, 20.0, 18.0, 1.8, 22.0, 0.0, 1.75, -16.50),
    ("TJX", "TJX Companies", "Consumer Cyclical", "Apparel Retail", 120.0, 133e9, 7.8e9, 28.0, 25.0, 2.2, 18.0, 60.0, 1.25, 6.80),
    ("BKNG", "Booking Holdings", "Consumer Cyclical", "Travel Services", 4800.0, 165e9, 8.5e9, 28.0, 22.0, 1.2, 25.0, 200.0, 0.85, 28.50),
    ("CMG", "Chipotle Mexican Grill", "Consumer Cyclical", "Restaurants", 58.0, 78e9, 2.5e9, 52.0, 42.0, 2.8, 18.0, 45.0, 0.0, 8.50),
    # Real Estate
    ("PLD", "Prologis Inc.", "Real Estate", "REIT—Industrial", 108.0, 100e9, 5.5e9, 38.0, 35.0, 3.5, 3.0, 6.0, 3.15, 52.50),
    ("AMT", "American Tower", "Real Estate", "REIT—Specialty", 192.0, 88e9, 6.5e9, 42.0, 38.0, 3.0, 4.0, 20.0, 3.05, 18.50),
    ("EQIX", "Equinix Inc.", "Real Estate", "REIT—Specialty", 850.0, 80e9, 3.8e9, 75.0, 65.0, 2.5, 3.0, 8.0, 1.85, 145.00),
    ("O", "Realty Income Corp.", "Real Estate", "REIT—Retail", 55.0, 48e9, 3.5e9, 52.0, 42.0, 3.5, 2.5, 4.0, 5.55, 28.50),
]


def seed_database(db: Session) -> dict:
    """Seed the database with sample financial data.

    Returns stats dict.
    """
    today = datetime.date.today()
    stats = {"companies": 0, "financials": 0}

    for row in SEED_COMPANIES:
        (symbol, name, sector, industry, ask, market_cap, ebitda,
         pe_ttm, pe_ftm, peg, roa, roe, div_yield, book_value) = row

        # Upsert company
        company = db.exec(select(Company).where(Company.symbol == symbol)).first()
        if not company:
            company = Company(symbol=symbol, name=name, sector=sector, industry=industry)
            db.add(company)
            db.commit()
            db.refresh(company)
            stats["companies"] += 1

        # Check for existing financial data today
        existing = db.exec(
            select(FinancialData).where(
                FinancialData.company_id == company.id,
                FinancialData.record_date == today,
            )
        ).first()

        fd = existing or FinancialData(company_id=company.id, symbol=symbol, record_date=today)

        fd.ask = ask
        fd.book_value = book_value
        fd.market_cap = market_cap
        fd.ebitda = ebitda if ebitda > 0 else None
        fd.pe_ratio_ttm = pe_ttm if pe_ttm > 0 else None
        fd.pe_ratio_ftm = pe_ftm if pe_ftm > 0 else None
        fd.peg_ratio = peg if peg > 0 else None
        fd.return_on_assets = roa if roa != 0 else None
        fd.return_on_equity = roe if roe != 0 else None
        fd.dividend_yield = div_yield if div_yield > 0 else None

        # Calculated metrics
        if fd.pe_ratio_ttm and fd.peg_ratio and fd.peg_ratio > 0:
            fd.garp_ratio = round(fd.pe_ratio_ttm / fd.peg_ratio, 2)

        db.add(fd)
        if not existing:
            stats["financials"] += 1

    db.commit()
    return stats
