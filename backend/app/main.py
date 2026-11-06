import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import auth, items
from app.seed import seed_db

MAX_REQUEST_BODY_SIZE = 1_048_576


class RequestBodyLimitMiddleware:
    def __init__(self, app, max_body_size: int = MAX_REQUEST_BODY_SIZE):
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        messages = []
        body_size = 0
        while True:
            message = await receive()
            messages.append(message)
            if message["type"] == "http.request":
                body_size += len(message.get("body", b""))
                if body_size > self.max_body_size:
                    body = b'{"detail":"Request body too large"}'
                    await send(
                        {
                            "type": "http.response.start",
                            "status": 413,
                            "headers": [
                                (b"content-type", b"application/json"),
                                (b"content-length", str(len(body)).encode("ascii")),
                            ],
                        }
                    )
                    await send({"type": "http.response.body", "body": body})
                    return
                if not message.get("more_body", False):
                    break
            else:
                break

        replay_index = 0

        async def replay_receive():
            nonlocal replay_index
            if replay_index < len(messages):
                message = messages[replay_index]
                replay_index += 1
                return message
            return await receive()

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
