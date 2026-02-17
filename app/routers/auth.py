from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_db
from app.models.user import User, UserCreate, UserRead
from app.services.auth import create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenResponse(UserRead):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        email=payload.email,
        password_hash=User.hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user)
    return TokenResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        access_token=token,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserCreate, db: Session = Depends(get_db)):
    user = db.exec(select(User).where(User.email == payload.email)).first()
    if not user or not user.verify_password(payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user)
    return TokenResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        access_token=token,
    )


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
