from app.auth import verify_password
from app.models import Item, User
from app.seed import MOCK_ITEMS, MOCK_USERS, seed_db


def clear_seed_data(db_session):
    db_session.query(Item).delete()
    db_session.query(User).delete()
    db_session.commit()


def test_seed_db_does_not_create_demo_users_outside_development(
    db_session, monkeypatch
):
    clear_seed_data(db_session)
    monkeypatch.setenv("APP_ENV", "production")

    seed_db(db_session)

    assert db_session.query(User).count() == 0
    items = db_session.query(Item).all()
    assert {item.sku for item in items} == {item["sku"] for item in MOCK_ITEMS}
    assert all(item.created_by_id is None for item in items)


def test_seed_db_creates_demo_users_in_development(db_session, monkeypatch):
    clear_seed_data(db_session)
    monkeypatch.setenv("APP_ENV", "development")

    seed_db(db_session)

    users = {user.username: user for user in db_session.query(User).all()}
    assert set(users) == {user["username"] for user in MOCK_USERS}
    for user_data in MOCK_USERS:
        stored_password = users[user_data["username"]].hashed_password
        assert stored_password != user_data["password"]
        assert verify_password(user_data["password"], stored_password)

    items = db_session.query(Item).all()
    assert {item.sku for item in items} == {item["sku"] for item in MOCK_ITEMS}
    assert all(item.created_by_id == users["admin"].id for item in items)


@pytest.mark.parametrize("app_env", ["development", "production"])
def test_seed_db_is_safe_to_call_repeatedly(db_session, monkeypatch, app_env):
    clear_seed_data(db_session)
    monkeypatch.setenv("APP_ENV", app_env)

    seed_db(db_session)
    seed_db(db_session)

    expected_usernames = (
        {user["username"] for user in MOCK_USERS}
        if app_env == "development"
        else set()
    )
    users = {user.username: user for user in db_session.query(User).all()}
    assert set(users) == expected_usernames

    items = db_session.query(Item).all()
    assert len(items) == len(MOCK_ITEMS)
    assert {item.sku for item in items} == {item["sku"] for item in MOCK_ITEMS}
    if app_env == "development":
        assert all(item.created_by_id == users["admin"].id for item in items)
    else:
        assert all(item.created_by_id is None for item in items)
