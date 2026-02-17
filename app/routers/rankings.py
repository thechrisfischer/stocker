from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import SQLModel, Session

from app.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.rankings import STRATEGIES, get_rankings


class StrategyInfo(SQLModel):
    key: str
    name: str
    description: str


class RankingEntry(SQLModel):
    symbol: str
    name: str | None
    score: float | None
    rank: int
    pe_ratio_ttm: float | None = None
    pe_ratio_ftm: float | None = None
    garp_ratio: float | None = None
    peg_ratio: float | None = None
    return_on_assets: float | None = None


router = APIRouter(prefix="/api/rankings", tags=["rankings"])


@router.get("/strategies", response_model=list[StrategyInfo])
def list_strategies(current_user: User = Depends(get_current_user)):
    return [
        StrategyInfo(key=key, name=info["name"], description=info["description"])
        for key, info in STRATEGIES.items()
    ]


@router.get("/{strategy}", response_model=list[RankingEntry])
def get_ranking(
    strategy: str,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if strategy not in STRATEGIES:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown strategy '{strategy}'. Use /api/rankings/strategies to list available strategies.",
        )

    results = get_rankings(db, strategy, limit=limit)
    return results
