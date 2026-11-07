from collections import OrderedDict
from dataclasses import dataclass
import logging
import math
import time
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, verify_password
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@dataclass
class _FailureState:
    count: int
    last_failure: float
    blocked_until: float = 0.0


class _LoginRateLimiter:
    def __init__(
        self,
        threshold: int = 5,
        base_delay: int = 1,
        max_delay: int = 300,
        reset_after: int = 3600,
        max_entries: int = 10_000,
        clock=time.monotonic,
    ):
        self._threshold = threshold
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._reset_after = reset_after
        self._max_entries = max_entries
        self._clock = clock
        self._states: OrderedDict[tuple[str, str], _FailureState] = OrderedDict()
        self._lock = Lock()

    def retry_after(self, keys: list[tuple[str, str]]) -> int:
        now = self._clock()
        remaining = 0.0
        with self._lock:
            for key in keys:
                state = self._states.get(key)
                if state is None:
                    continue
                if now - state.last_failure >= self._reset_after:
                    del self._states[key]
                    continue
                self._states.move_to_end(key)
                remaining = max(remaining, state.blocked_until - now)
        return math.ceil(remaining) if remaining > 0 else 0

    def record_failure(self, keys: list[tuple[str, str]]) -> None:
        now = self._clock()
        with self._lock:
            for key in keys:
                state = self._states.get(key)
                if state is None or now - state.last_failure >= self._reset_after:
                    if state is None and len(self._states) >= self._max_entries:
                        self._states.popitem(last=False)
                    state = _FailureState(count=0, last_failure=now)
                    self._states[key] = state
                state.count += 1
                state.last_failure = now
                self._states.move_to_end(key)
                if state.count >= self._threshold:
                    exponent = min(state.count - self._threshold, 30)
                    delay = min(self._base_delay * (2**exponent), self._max_delay)
                    state.blocked_until = now + delay
                    logger.warning(
                        "Repeated failed login attempts triggered a temporary rate limit"
                    )

    def reset(self, key: tuple[str, str]) -> None:
        with self._lock:
            self._states.pop(key, None)


_login_rate_limiter = _LoginRateLimiter()


def _login(db: Session, username: str, password: str, client_ip: str) -> Token:
    account_key = ("account", username.strip().casefold()[:256])
    ip_key = ("ip", client_ip)
    keys = [account_key, ip_key]
    retry_after = _login_rate_limiter.retry_after(keys)
    if retry_after:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        _login_rate_limiter.record_failure(keys)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    _login_rate_limiter.reset(account_key)
    return Token(access_token=create_access_token(user.username))


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else "unknown"
    return _login(db, form_data.username, form_data.password, client_ip)


@router.post("/login/json", response_model=Token)
def login_json(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    return _login(db, body.username, body.password, client_ip)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
