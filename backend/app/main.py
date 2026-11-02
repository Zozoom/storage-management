import logging
import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from threading import Lock
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, items
from app.seed import seed_db


logger = logging.getLogger(__name__)
_LOGIN_RATE_LIMIT = 30
_LOGIN_RATE_WINDOW_SECONDS = 60
_MAX_TRACKED_LOGIN_IPS = 10_000


@dataclass
class _LoginBucket:
    attempts: deque[float] = field(default_factory=deque)
    alerted: bool = False


_login_attempts: OrderedDict[str, _LoginBucket] = OrderedDict()
_login_attempts_lock = Lock()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if os.getenv("TESTING") != "1":
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_db(db)
        finally:
            db.close()
    yield


app = FastAPI(
    title="Storage Management API",
    description="Simple stock management with JWT auth",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def limit_login_requests(request: Request, call_next):
    if request.url.path not in {"/api/auth/login", "/api/auth/login/json"}:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    limited = False
    retry_after = 1
    with _login_attempts_lock:
        bucket = _login_attempts.get(client_ip)
        if bucket is None:
            if len(_login_attempts) >= _MAX_TRACKED_LOGIN_IPS:
                _login_attempts.popitem(last=False)
            bucket = _LoginBucket()
            _login_attempts[client_ip] = bucket
        _login_attempts.move_to_end(client_ip)

        cutoff = now - _LOGIN_RATE_WINDOW_SECONDS
        while bucket.attempts and bucket.attempts[0] <= cutoff:
            bucket.attempts.popleft()
        if len(bucket.attempts) < _LOGIN_RATE_LIMIT:
            bucket.alerted = False
            bucket.attempts.append(now)
        else:
            limited = True
            retry_after = max(
                1,
                int(bucket.attempts[0] + _LOGIN_RATE_WINDOW_SECONDS - now + 0.999),
            )
            if not bucket.alerted:
                logger.warning("Login request rate limit exceeded for IP %s", client_ip)
                bucket.alerted = True

    if limited:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many login attempts. Please try again later."},
            headers={"Retry-After": str(retry_after)},
        )
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(items.router)


@app.get("/health")
def health():
    return {"status": "ok"}
