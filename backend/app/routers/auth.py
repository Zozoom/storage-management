import math
import time
from collections import deque
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    get_current_user,
    oauth2_scheme,
    revoke_access_token,
    verify_password,
)
from app.database import get_db
from app.models import User
from app.schemas import (
    MAX_PASSWORD_LENGTH,
    MAX_USERNAME_LENGTH,
    LoginRequest,
    Token,
    UserOut,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

LOGIN_RATE_WINDOW_SECONDS = 60
LOGIN_IP_RATE_LIMIT = 20
LOGIN_ACCOUNT_RATE_LIMIT = 5
_login_attempts: dict[tuple[str, str], deque[float]] = {}
_login_attempts_lock = Lock()


def _check_login_rate_limit(request: Request, username: str) -> None:
    now = time.monotonic()
    client_ip = request.client.host if request.client else "unknown"
    keys = (
        ("ip", client_ip),
        ("account", f"{client_ip}\0{username.casefold()}"),
    )
    limits = (LOGIN_IP_RATE_LIMIT, LOGIN_ACCOUNT_RATE_LIMIT)

    with _login_attempts_lock:
        for key, timestamps in list(_login_attempts.items()):
            while timestamps and now - timestamps[0] >= LOGIN_RATE_WINDOW_SECONDS:
                timestamps.popleft()
            if not timestamps:
                del _login_attempts[key]

        retry_after = 0.0
        for key, limit in zip(keys, limits):
            timestamps = _login_attempts.get(key)
            if timestamps and len(timestamps) >= limit:
                retry_after = max(
                    retry_after,
                    LOGIN_RATE_WINDOW_SECONDS - (now - timestamps[0]),
                )

        if retry_after:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Try again later.",
                headers={"Retry-After": str(max(1, math.ceil(retry_after)))},
            )

        for key in keys:
            _login_attempts.setdefault(key, deque()).append(now)


def _login(db: Session, username: str, password: str) -> Token:
    if len(username) > MAX_USERNAME_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username or password exceeds the maximum length",
        )
    user = db.query(User).filter(User.username == username).first()
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user is None:
        raise credentials_exc
    if not verify_password(password, user.hashed_password):
        raise credentials_exc
    return Token(access_token=create_access_token(user.username))


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    _check_login_rate_limit(request, form_data.username)
    return _login(db, form_data.username, form_data.password)


@router.post("/login/json", response_model=Token)
def login_json(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    _check_login_rate_limit(request, body.username)
    return _login(db, body.username, body.password)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    token: str = Depends(oauth2_scheme),
    _: User = Depends(get_current_user),
):
    revoke_access_token(token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
