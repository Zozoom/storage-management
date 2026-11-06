import os

os.environ["TESTING"] = "1"
os.environ["SECRET_KEY"] = "test-only-secret-key-with-sufficient-length"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.database import Base, get_db
from app.main import app
from app.models import Item, User


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSession()

    user = User(username="admin", hashed_password=hash_password("admin123"))
    session.add(user)
    session.flush()
    session.add(
        Item(
            sku="TEST-1",
            name="Test Item",
            description="Fixture item",
            quantity=10,
            location="Z-01",
            min_stock=5,
            created_by_id=user.id,
        )
    )
    session.commit()

    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers():
    token = create_access_token("admin")
    return {"Authorization": f"Bearer {token}"}
