from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.model.database import get_db, settings
from app.model.entities import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token jest nieprawidłowy lub wygasł",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_error

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id = int(payload.get("sub", ""))
    except (JWTError, ValueError):
        raise credentials_error

    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_error
    return user
