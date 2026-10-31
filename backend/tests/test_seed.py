from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import verify_password
from app.database import Base
from app.models import Item, User
from app.seed import seed_db


def _empty_database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, session_factory


def test_seeded_users_have_verifiable_password_hashes():
    engine, session_factory = _empty_database()
    try:
        with session_factory() as db:
            seed_db(db)
            users = {user.username: user for user in db.query(User).all()}

            assert set(users) == {"admin", "clerk"}
            for username, password in (("admin", "admin123"), ("clerk", "clerk123")):
                hashed_password = users[username].hashed_password
                assert hashed_password != password
                assert verify_password(password, hashed_password)
    finally:
        engine.dispose()


def test_seeded_inventory_has_expected_records_and_creators():
    engine, session_factory = _empty_database()
    try:
        with session_factory() as db:
            seed_db(db)
            items = db.query(Item).all()

            assert {
                (item.sku, item.name, item.quantity, item.location, item.min_stock)
                for item in items
            } == {
                ("WDG-001", "Widget", 50, "A-01", 10),
                ("BOLT-M8", "M8 Bolt", 200, "B-01", 50),
                ("BOX-S", "Small Box", 3, "C-01", 10),
            }
            assert len(items) == 3
            assert all(item.created_by is not None for item in items)
            assert all(item.created_by.username == "admin" for item in items)
    finally:
        engine.dispose()


def test_seed_commits_successfully_to_an_empty_database():
    engine, session_factory = _empty_database()
    try:
        with session_factory() as db:
            assert db.query(User).count() == 0
            assert db.query(Item).count() == 0
            seed_db(db)

        with session_factory() as db:
            assert db.query(User).count() == 2
            assert db.query(Item).count() == 3
    finally:
        engine.dispose()
