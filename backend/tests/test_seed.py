from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import verify_password
from app.database import Base
from app.models import Item, User
from app.seed import MOCK_ITEMS, MOCK_USERS, seed_db


def test_seed_db_creates_users_with_hashed_demo_passwords(monkeypatch):
    monkeypatch.setenv("TESTING", "1")
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    with session_factory() as db:
        seed_db(db)

        users = {user.username: user for user in db.query(User).all()}
        assert set(users) == {user["username"] for user in MOCK_USERS}
        for credentials in MOCK_USERS:
            user = users[credentials["username"]]
            assert user.hashed_password != credentials["password"]
            assert verify_password(credentials["password"], user.hashed_password)

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_seed_db_creates_inventory_with_expected_values_and_creator(monkeypatch):
    monkeypatch.setenv("TESTING", "1")
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    with session_factory() as db:
        seed_db(db)

        items = {item.sku: item for item in db.query(Item).all()}
        assert set(items) == {item["sku"] for item in MOCK_ITEMS}
        admin = db.query(User).filter_by(username="admin").one()
        for expected in MOCK_ITEMS:
            item = items[expected["sku"]]
            for field in ("name", "quantity", "location", "min_stock"):
                assert getattr(item, field) == expected[field]
            assert item.created_by_id == admin.id
            assert item.created_by.username == "admin"

    Base.metadata.drop_all(bind=engine)
    engine.dispose()
