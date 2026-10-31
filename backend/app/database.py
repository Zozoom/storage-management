import tempfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# A temporary file preserves process-local, transient data while allowing the
# connection pool to give each concurrent session its own SQLite connection.
_database_dir = tempfile.TemporaryDirectory(prefix="storage-management-")
_database_path = Path(_database_dir.name) / "storage.db"
engine = create_engine(
    f"sqlite:///{_database_path.as_posix()}",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
