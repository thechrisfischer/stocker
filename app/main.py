from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_db_and_tables
from app.models import User, Company, FinancialData  # noqa: F401 — ensure models registered before create_all
from app.routers import auth, companies, rankings


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
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

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(rankings.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
