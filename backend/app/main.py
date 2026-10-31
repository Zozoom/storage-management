import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, items
from app.seed import seed_db


MAX_REQUEST_BODY_BYTES = 1024 * 1024


class RequestBodyLimitMiddleware:
    def __init__(self, app, max_body_size: int = MAX_REQUEST_BODY_BYTES):
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        content_length = next(
            (
                value
                for name, value in scope.get("headers", [])
                if name.lower() == b"content-length"
            ),
            None,
        )
        if content_length is not None:
            try:
                if int(content_length) > self.max_body_size:
                    response = PlainTextResponse("Request body too large", status_code=413)
                    await response(scope, receive, send)
                    return
            except ValueError:
                pass

        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            if message["type"] != "http.request":
                continue

            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.max_body_size:
                response = PlainTextResponse("Request body too large", status_code=413)
                await response(scope, receive, send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break

        body_bytes = bytes(body)
        body_sent = False

        async def replay_body():
            nonlocal body_sent
            if body_sent:
                return {"type": "http.disconnect"}
            body_sent = True
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        await self.app(scope, replay_body, send)


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestBodyLimitMiddleware)

app.include_router(auth.router)
app.include_router(items.router)


@app.get("/health")
def health():
    return {"status": "ok"}
