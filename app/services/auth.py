from datetime import datetime, timedelta, timezone

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from app.config import settings
from app.database import get_db
from app.models.user import User

security = HTTPBearer()

_serializer = URLSafeTimedSerializer(settings.secret_key)


def create_access_token(user: User) -> str:
    return _serializer.dumps({"sub": str(user.id), "email": user.email})


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        max_age = settings.token_expire_minutes * 60
        payload = _serializer.loads(token, max_age=max_age)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except (BadSignature, SignatureExpired):
        raise credentials_exception

    user = db.exec(select(User).where(User.id == int(user_id))).first()
    if user is None:
        raise credentials_exception
    return user
