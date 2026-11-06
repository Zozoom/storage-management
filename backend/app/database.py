from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# In-memory only: pooled connections share the database within this process.
# SQLite still limits concurrent writes; use a production database for multi-worker use.
engine = create_engine(
    "sqlite:///file:storage-management?mode=memory&cache=shared&uri=true",
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
