import logging
import time
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, verify_password
from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])
SESSION_COOKIE = "storage_session"

logger = logging.getLogger(__name__)
_ACCOUNT_FAILURE_THRESHOLD = 5
_ACCOUNT_FAILURE_WINDOW_SECONDS = 15 * 60
_MAX_ACCOUNT_LOCKOUT_SECONDS = 5 * 60
_MAX_TRACKED_ACCOUNTS = 10_000
_account_attempts: dict[str, tuple[int, float, float]] = {}
_account_attempts_lock = Lock()


def _check_account_lockout(username: str) -> None:
    now = time.monotonic()
    with _account_attempts_lock:
        attempt = _account_attempts.get(username)
        if not attempt:
            return
        failures, last_failure, locked_until = attempt
        if now - last_failure > _ACCOUNT_FAILURE_WINDOW_SECONDS:
            _account_attempts.pop(username, None)
            return
        if locked_until > now:
            retry_after = max(1, int(locked_until - now + 0.999))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
                headers={"Retry-After": str(retry_after)},
            )


def _record_failed_login(username: str) -> None:
    now = time.monotonic()
    with _account_attempts_lock:
        attempt = _account_attempts.get(username)
        if attempt and now - attempt[1] <= _ACCOUNT_FAILURE_WINDOW_SECONDS:
            failures = attempt[0] + 1
        else:
            failures = 1

        locked_until = 0.0
        if failures >= _ACCOUNT_FAILURE_THRESHOLD:
            delay = min(2 ** (failures - _ACCOUNT_FAILURE_THRESHOLD), _MAX_ACCOUNT_LOCKOUT_SECONDS)
            locked_until = now + delay
            logger.warning("Repeated failed login attempts for account %r", username)

        if username not in _account_attempts and len(_account_attempts) >= _MAX_TRACKED_ACCOUNTS:
            _account_attempts.pop(next(iter(_account_attempts)))
        _account_attempts[username] = (failures, now, locked_until)


def _clear_failed_logins(username: str) -> None:
    with _account_attempts_lock:
        _account_attempts.pop(username, None)


def _login(db: Session, username: str, password: str) -> str:
    _check_account_lockout(username)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        _record_failed_login(username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(password, user.hashed_password):
        _record_failed_login(username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _clear_failed_logins(username)
    return create_access_token(user.username)


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        max_age=settings.access_token_expire_minutes * 60,
        path="/api",
        secure=True,
        httponly=True,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"


@router.post("/login")
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    _set_session_cookie(response, _login(db, form_data.username, form_data.password))
    return {"message": "Login successful"}


@router.post("/login/json")
def login_json(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    _set_session_cookie(response, _login(db, body.username, body.password))
    return {"message": "Login successful"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(
        key=SESSION_COOKIE,
        path="/api",
        secure=True,
        httponly=True,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
