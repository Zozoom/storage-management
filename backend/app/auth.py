from datetime import datetime, timedelta, timezone
from threading import Lock
from time import time
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
_revoked_tokens: dict[str, float] = {}
_revoked_tokens_lock = Lock()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expire, "jti": uuid4().hex},
        settings.secret_key,
        algorithm="HS256",
    )


def revoke_access_token(token: str) -> None:
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    token_id = payload.get("jti")
    expires_at = payload.get("exp")
    if not isinstance(token_id, str) or not isinstance(expires_at, (int, float)):
        return

    now = time()
    with _revoked_tokens_lock:
        for revoked_id, expiry in list(_revoked_tokens.items()):
            if expiry <= now:
                del _revoked_tokens[revoked_id]
        _revoked_tokens[token_id] = float(expires_at)


def _is_token_revoked(token_id: str) -> bool:
    now = time()
    with _revoked_tokens_lock:
        for revoked_id, expiry in list(_revoked_tokens.items()):
            if expiry <= now:
                del _revoked_tokens[revoked_id]
        return token_id in _revoked_tokens


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        username: str | None = payload.get("sub")
        token_id = payload.get("jti")
        if not username or not isinstance(token_id, str) or _is_token_revoked(token_id):
            raise credentials_exc
    except JWTError as exc:
        raise credentials_exc from exc

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise credentials_exc
    return user
