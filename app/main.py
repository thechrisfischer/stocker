import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select

from app.config import settings
from app.database import create_db_and_tables, get_db
from app.models import User, Company, FinancialData  # noqa: F401 — ensure models registered before create_all
from app.routers import auth, companies, rankings
from app.routers.pages import router as pages_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    # Auto-seed if database is empty
    db = next(get_db())
    company_count = db.exec(select(Company)).first()
    if not company_count:
        logger.info("Empty database detected — seeding with sample data...")
        from app.services.seed_data import seed_database
        from app.services.data_import import compute_rankings
        stats = seed_database(db)
        logger.info(f"Seeded: {stats}")
        ranked = compute_rankings(db)
        logger.info(f"Ranked {ranked} records")

    yield


app = FastAPI(
    title="StockRocker API",
    description="Stock analysis and investment research — ranking companies by financial metrics.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML pages (served at /, /login, /register, /logout)
app.include_router(pages_router)

# JSON API
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(rankings.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
