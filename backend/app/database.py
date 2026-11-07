from threading import Lock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool

# In-memory only: data lives in the process and is reseeded on every start.
# shortcut: one shared connection, single worker only; use a real DB if data must persist or scale.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
_db_lock = Lock()


class Base(DeclarativeBase):
    pass


def get_db():
    _db_lock.acquire()
    try:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    finally:
        _db_lock.release()
