"""
HTML page routes for the web frontend.

Serves Jinja2 templates for the public-facing website.
Auth is handled via cookies (token stored in a secure cookie).
"""

from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, func

from app.database import get_db
from app.models.company import Company
from app.models.financial_data import FinancialData
from app.models.user import User
from app.services.auth import create_access_token, _serializer
from app.config import settings
from app.services.rankings import STRATEGIES, get_rankings

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["pages"])


def _get_user_from_cookie(request: Request, db: Session) -> Optional[User]:
    """Try to extract the current user from the auth cookie."""
    token = request.cookies.get("token")
    if not token:
        return None
    try:
        max_age = settings.token_expire_minutes * 60
        payload = _serializer.loads(token, max_age=max_age)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return db.exec(select(User).where(User.id == int(user_id))).first()
    except Exception:
        return None


@router.get("/", response_class=HTMLResponse)
def home_page(request: Request, db: Session = Depends(get_db)):
    user = _get_user_from_cookie(request, db)

    # Get stats
    company_count = db.exec(select(func.count(Company.id))).first() or 0
    latest_date = db.exec(select(func.max(FinancialData.record_date))).first()

    stats = {
        "companies": company_count,
        "strategies": len(STRATEGIES),
        "last_updated": str(latest_date) if latest_date else None,
    }

    # Build ranking data for each strategy
    strategy_data = []
    for key, info in STRATEGIES.items():
        rankings = get_rankings(db, key, limit=25) if company_count > 0 else []
        strategy_data.append({
            "key": key,
            "name": info["name"],
            "description": info["description"],
            "rankings": rankings,
        })

    return templates.TemplateResponse("home.html", {
        "request": request,
        "user": user,
        "stats": stats,
        "strategies": strategy_data,
    })


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = _get_user_from_cookie(request, db)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "user": None,
        "error": None,
    })


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.exec(select(User).where(User.email == email)).first()
    if not user or not user.verify_password(password):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "user": None,
            "error": "Invalid email or password",
        })

    token = create_access_token(user)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="token", value=token,
        httponly=True, samesite="lax",
        max_age=settings.token_expire_minutes * 60,
    )
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    user = _get_user_from_cookie(request, db)
    if user:
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("register.html", {
        "request": request,
        "user": None,
        "error": None,
    })


@router.post("/register", response_class=HTMLResponse)
def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    existing = db.exec(select(User).where(User.email == email)).first()
    if existing:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "user": None,
            "error": "An account with this email already exists",
        })

    user = User(
        email=email,
        password_hash=User.hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="token", value=token,
        httponly=True, samesite="lax",
        max_age=settings.token_expire_minutes * 60,
    )
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("token")
    return response
