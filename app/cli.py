"""
CLI management commands for StockRocker.

Usage:
    python -m app.cli seed                   # Seed with sample data + compute rankings
    python -m app.cli import-stocks          # Fetch data for default stock list
    python -m app.cli import-stocks AAPL MSFT # Fetch specific symbols
    python -m app.cli compute-rankings       # Recompute all rankings
"""

import argparse
import logging
import sys

from app.database import create_db_and_tables, get_db
from app.models import User, Company, FinancialData  # noqa: F401
from app.services.data_import import fetch_and_store, compute_rankings, SEED_SYMBOLS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def cmd_seed(args):
    from app.services.seed_data import seed_database

    create_db_and_tables()
    db = next(get_db())

    logger.info("Seeding database with sample data...")
    stats = seed_database(db)
    logger.info(f"Seed complete: {stats}")

    logger.info("Computing rankings...")
    n = compute_rankings(db)
    logger.info(f"Ranked {n} records")


def cmd_import(args):
    create_db_and_tables()
    db = next(get_db())

    symbols = args.symbols if args.symbols else None
    logger.info(f"Importing {len(symbols or SEED_SYMBOLS)} stocks...")

    stats = fetch_and_store(db, symbols)
    logger.info(f"Import complete: {stats}")

    logger.info("Computing rankings...")
    n = compute_rankings(db)
    logger.info(f"Ranked {n} records")


def cmd_rankings(args):
    create_db_and_tables()
    db = next(get_db())

    logger.info("Computing rankings...")
    n = compute_rankings(db)
    logger.info(f"Ranked {n} records")


def main():
    parser = argparse.ArgumentParser(description="StockRocker CLI")
    sub = parser.add_subparsers(dest="command")

    p_seed = sub.add_parser("seed", help="Seed database with sample data")
    p_seed.set_defaults(func=cmd_seed)

    p_import = sub.add_parser("import-stocks", help="Fetch stock data from Yahoo Finance")
    p_import.add_argument("symbols", nargs="*", help="Stock symbols (default: built-in list)")
    p_import.set_defaults(func=cmd_import)

    p_rank = sub.add_parser("compute-rankings", help="Recompute rankings")
    p_rank.set_defaults(func=cmd_rankings)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
