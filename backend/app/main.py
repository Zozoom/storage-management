import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, items
from app.seed import seed_db


MAX_REQUEST_BODY_BYTES = 16 * 1024


class RequestBodyLimitMiddleware:
    def __init__(self, app, max_body_size: int = MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > self.max_body_size:
                response = JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large"},
                )
                await response(scope, receive, send)
                return
            if not message.get("more_body", False):
                break

        request_body = bytes(body)
        body_sent = False

        async def replay_receive():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": request_body, "more_body": False}
            return {"type": "http.request", "body": b"", "more_body": False}

        await self.app(scope, replay_receive, send)


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

app.add_middleware(RequestBodyLimitMiddleware)
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
