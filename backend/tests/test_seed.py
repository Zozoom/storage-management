import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import verify_password
from app.database import Base
from app.models import Item, User
from app.seed import seed_db


@pytest.fixture()
def seed_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_development_seeds_demo_users_and_items(seed_session, monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("VERCEL_ENV", "development")

    seed_db(seed_session)

    users = {user.username: user for user in seed_session.query(User).all()}
    assert set(users) == {"admin", "clerk"}
    for username, password in (("admin", "admin123"), ("clerk", "clerk123")):
        assert users[username].hashed_password != password
        assert verify_password(password, users[username].hashed_password)

    items = {
        item.sku: item
        for item in seed_session.query(Item).all()
    }
    assert set(items) == {"WDG-001", "BOLT-M8", "BOX-S"}
    assert {
        sku: {
            "name": item.name,
            "quantity": item.quantity,
            "location": item.location,
            "min_stock": item.min_stock,
            "description": item.description,
        }
        for sku, item in items.items()
    } == {
        "WDG-001": {
            "name": "Widget",
            "quantity": 50,
            "location": "A-01",
            "min_stock": 10,
            "description": None,
        },
        "BOLT-M8": {
            "name": "M8 Bolt",
            "quantity": 200,
            "location": "B-01",
            "min_stock": 50,
            "description": None,
        },
        "BOX-S": {
            "name": "Small Box",
            "quantity": 3,
            "location": "C-01",
            "min_stock": 10,
            "description": None,
        },
    }
    assert all(item.created_by_id == users["admin"].id for item in items.values())


def test_production_seeds_only_configured_admin(seed_session, monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    monkeypatch.setenv("INITIAL_ADMIN_USERNAME", "warehouse-admin")
    monkeypatch.setenv("INITIAL_ADMIN_PASSWORD", "deployment-secret-123")

    seed_db(seed_session)

    users = seed_session.query(User).all()
    assert [user.username for user in users] == ["warehouse-admin"]
    assert verify_password("deployment-secret-123", users[0].hashed_password)
    assert not verify_password("admin123", users[0].hashed_password)
    assert seed_session.query(Item).count() == 3


def test_production_requires_deployment_credentials(seed_session, monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    monkeypatch.delenv("INITIAL_ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("INITIAL_ADMIN_PASSWORD", raising=False)

    with pytest.raises(RuntimeError, match="Production seeding requires"):
        seed_db(seed_session)

    assert seed_session.query(User).count() == 0
    assert seed_session.query(Item).count() == 0
