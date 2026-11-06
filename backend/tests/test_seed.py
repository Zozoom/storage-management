import pytest

from app.auth import verify_password
from app.models import Item, User
from app.seed import seed_db


def test_seed_db_does_not_create_demo_users_in_production(db_session, monkeypatch):
    monkeypatch.setenv("APP_MODE", "production")
    before = db_session.query(User).count()

    seed_db(db_session)

    assert db_session.query(User).count() == before


def test_demo_mode_requires_credentials(db_session, monkeypatch):
    monkeypatch.setenv("APP_MODE", "demo")
    for name in (
        "DEMO_ADMIN_USERNAME",
        "DEMO_ADMIN_PASSWORD",
        "DEMO_CLERK_USERNAME",
        "DEMO_CLERK_PASSWORD",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(RuntimeError, match="DEMO_ADMIN_USERNAME"):
        seed_db(db_session)


def test_demo_mode_seeds_users_items_and_hashed_passwords(db_session, monkeypatch):
    db_session.query(Item).delete()
    db_session.query(User).delete()
    db_session.commit()

    monkeypatch.setenv("APP_MODE", "demo")
    monkeypatch.setenv("DEMO_ADMIN_USERNAME", "warehouse-admin")
    monkeypatch.setenv("DEMO_ADMIN_PASSWORD", "admin-demo-password-1234")
    monkeypatch.setenv("DEMO_CLERK_USERNAME", "warehouse-clerk")
    monkeypatch.setenv("DEMO_CLERK_PASSWORD", "clerk-demo-password-5678")

    seed_db(db_session)

    users = {user.username: user for user in db_session.query(User).all()}
    assert set(users) == {"warehouse-admin", "warehouse-clerk"}

    admin = users["warehouse-admin"]
    clerk = users["warehouse-clerk"]
    assert admin.hashed_password != "admin-demo-password-1234"
    assert clerk.hashed_password != "clerk-demo-password-5678"
    assert verify_password("admin-demo-password-1234", admin.hashed_password)
    assert verify_password("clerk-demo-password-5678", clerk.hashed_password)

    items = db_session.query(Item).order_by(Item.sku).all()
    assert [
        (item.sku, item.name, item.quantity, item.location, item.min_stock)
        for item in items
    ] == [
        ("BOLT-M8", "M8 Bolt", 200, "B-01", 50),
        ("BOX-S", "Small Box", 3, "C-01", 10),
        ("WDG-001", "Widget", 50, "A-01", 10),
    ]
    assert all(item.created_by_id == admin.id for item in items)
    assert all(item.created_by.username == "warehouse-admin" for item in items)
