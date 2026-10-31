import asyncio
import hashlib
import logging
import math
import os
import threading
import time
from collections import OrderedDict, deque
from typing import Deque

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user, verify_password
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, Token, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

logger = logging.getLogger(__name__)
LOGIN_FAILURE_WINDOW_SECONDS = 15 * 60
LOGIN_FAILURE_LIMIT = 5
PROGRESSIVE_DELAY_BASE_SECONDS = 0.25
PROGRESSIVE_DELAY_MAX_SECONDS = 4.0
MAX_TRACKED_LOGIN_BUCKETS = 10_000
_DEMO_USERNAMES = frozenset({"admin", "clerk"})
_login_failures: OrderedDict[tuple[str, str], Deque[float]] = OrderedDict()
_login_failures_lock = threading.Lock()


def _account_bucket(username: str) -> tuple[str, str]:
    normalized = username.casefold().encode("utf-8", errors="replace")
    return "account", hashlib.sha256(normalized).hexdigest()


def _failure_buckets(client_ip: str, username: str) -> tuple[tuple[str, str], ...]:
    return (("ip", client_ip), _account_bucket(username))


def _prune_bucket(bucket: Deque[float], now: float) -> None:
    cutoff = now - LOGIN_FAILURE_WINDOW_SECONDS
    while bucket and bucket[0] <= cutoff:
        bucket.popleft()


def _get_bucket(key: tuple[str, str], now: float) -> Deque[float] | None:
    bucket = _login_failures.get(key)
    if bucket is None:
        return None
    _prune_bucket(bucket, now)
    if not bucket:
        del _login_failures[key]
        return None
    _login_failures.move_to_end(key)
    return bucket


def _throttle_retry_after(client_ip: str, username: str) -> int | None:
    now = time.monotonic()
    with _login_failures_lock:
        counts = []
        for key in _failure_buckets(client_ip, username):
            bucket = _get_bucket(key, now)
            counts.append(len(bucket) if bucket else 0)
            if bucket and len(bucket) >= LOGIN_FAILURE_LIMIT:
                return max(1, math.ceil(bucket[0] + LOGIN_FAILURE_WINDOW_SECONDS - now))
    return None


def _record_login_failure(client_ip: str, username: str) -> float:
    now = time.monotonic()
    counts = []
    with _login_failures_lock:
        for key in _failure_buckets(client_ip, username):
            bucket = _get_bucket(key, now)
            if bucket is None:
                if len(_login_failures) >= MAX_TRACKED_LOGIN_BUCKETS:
                    cutoff = now - LOGIN_FAILURE_WINDOW_SECONDS
                    for old_key, old_bucket in list(_login_failures.items()):
                        _prune_bucket(old_bucket, now)
                        if not old_bucket:
                            del _login_failures[old_key]
                while len(_login_failures) >= MAX_TRACKED_LOGIN_BUCKETS:
                    _login_failures.popitem(last=False)
                bucket = deque()
                _login_failures[key] = bucket
            bucket.append(now)
            _login_failures.move_to_end(key)
            counts.append(len(bucket))

    failure_count = max(counts, default=1)
    return min(
        PROGRESSIVE_DELAY_BASE_SECONDS * (2 ** (failure_count - 1)),
        PROGRESSIVE_DELAY_MAX_SECONDS,
    )


def _clear_login_failures(client_ip: str, username: str) -> None:
    with _login_failures_lock:
        for key in _failure_buckets(client_ip, username):
            _login_failures.pop(key, None)


def _is_production() -> bool:
    return any(
        os.getenv(name, "").strip().lower() == "production"
        for name in ("ENVIRONMENT", "APP_ENV", "VERCEL_ENV", "NODE_ENV")
    )


async def _authenticate(
    username: str,
    password: str,
    request: Request,
    db: Session,
    *,
    include_auth_challenge: bool = False,
) -> Token:
    client_ip = request.client.host if request.client else "unknown"
    account_hash = _account_bucket(username)[1]
    retry_after = _throttle_retry_after(client_ip, username)
    if retry_after is not None:
        logger.warning(
            "Login attempt throttled (ip=%s, account_hash=%s)",
            client_ip,
            account_hash,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    demo_account_disabled = (
        _is_production() and username.casefold() in _DEMO_USERNAMES
    )
    user = None if demo_account_disabled else (
        db.query(User).filter(User.username == username).first()
    )
    if not user or not verify_password(password, user.hashed_password):
        delay = _record_login_failure(client_ip, username)
        logger.warning(
            "Login attempt failed (ip=%s, account_hash=%s)",
            client_ip,
            account_hash,
        )
        await asyncio.sleep(delay)
        headers = {"WWW-Authenticate": "Bearer"} if include_auth_challenge else None
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers=headers,
        )

    _clear_login_failures(client_ip, username)
    return Token(access_token=create_access_token(user.username))


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return await _authenticate(
        form_data.username,
        form_data.password,
        request,
        db,
        include_auth_challenge=True,
    )


@router.post("/login/json", response_model=Token)
async def login_json(
    body: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    return await _authenticate(body.username, body.password, request, db)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
