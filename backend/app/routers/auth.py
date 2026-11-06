import hashlib
import math
import threading
import time
from dataclasses import dataclass
from typing import Callable

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, verify_password
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@dataclass
class _FailureState:
    failures: int
    last_failure: float
    blocked_until: float


class LoginRateLimiter:
    def __init__(
        self,
        window_seconds: int = 15 * 60,
        max_delay_seconds: int = 60,
        max_entries: int = 10_000,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.window_seconds = window_seconds
        self.max_delay_seconds = max_delay_seconds
        self.max_entries = max_entries
        self._clock = clock
        self._failures: dict[str, _FailureState] = {}
        self._lock = threading.Lock()

    @staticmethod
    def _key(category: str, value: str) -> str:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return f"{category}:{digest}"

    def _keys(self, ip_address: str, username: str) -> tuple[str, str]:
        return (
            self._key("ip", ip_address),
            self._key("account", username.casefold()),
        )

    def check(self, ip_address: str, username: str) -> int | None:
        now = self._clock()
        with self._lock:
            retry_after = 0.0
            for key in self._keys(ip_address, username):
                state = self._failures.get(key)
                if state is None:
                    continue
                if now - state.last_failure >= self.window_seconds:
                    del self._failures[key]
                    continue
                retry_after = max(retry_after, state.blocked_until - now)
            if retry_after > 0:
                return math.ceil(retry_after)
            return None

    def record_failure(self, ip_address: str, username: str) -> int:
        now = self._clock()
        with self._lock:
            self._remove_expired(now)
            retry_after = 0
            for key in self._keys(ip_address, username):
                state = self._failures.get(key)
                failures = state.failures + 1 if state else 1
                delay = min(2 ** (failures - 1), self.max_delay_seconds)
                self._failures[key] = _FailureState(
                    failures=failures,
                    last_failure=now,
                    blocked_until=now + delay,
                )
                retry_after = max(retry_after, delay)
            self._enforce_capacity()
            return retry_after

    def record_success(self, ip_address: str, username: str) -> None:
        with self._lock:
            for key in self._keys(ip_address, username):
                self._failures.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._failures.clear()

    def _remove_expired(self, now: float) -> None:
        expired = [
            key
            for key, state in self._failures.items()
            if now - state.last_failure >= self.window_seconds
        ]
        for key in expired:
            del self._failures[key]

    def _enforce_capacity(self) -> None:
        excess = len(self._failures) - self.max_entries
        if excess > 0:
            oldest = sorted(
                self._failures,
                key=lambda key: self._failures[key].last_failure,
            )[:excess]
            for key in oldest:
                del self._failures[key]


login_rate_limiter = LoginRateLimiter()


def _login(
    db: Session, username: str, password: str, ip_address: str
) -> Token:
    retry_after = login_rate_limiter.check(ip_address, username)
    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        retry_after = login_rate_limiter.record_failure(ip_address, username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer",
                "Retry-After": str(retry_after),
            },
        )

    login_rate_limiter.record_success(ip_address, username)
    return Token(access_token=create_access_token(user.username))


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return _login(db, form_data.username, form_data.password, _client_ip(request))


@router.post("/login/json", response_model=Token)
def login_json(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return _login(db, body.username, body.password, _client_ip(request))


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
