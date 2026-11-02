from fastapi import HTTPException
from jose import jwt

from app.auth import hash_password
from app.config import settings
from app.models import User
from app.routers.auth import _login


def test_login_selects_the_requested_existing_user(db_session):
    db_session.add(
        User(username="clerk", hashed_password=hash_password("clerk-password"))
    )
    db_session.commit()

    token = _login(db_session, "clerk", "clerk-password")
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])

    assert payload["sub"] == "clerk"


def test_login_rejects_unknown_user_instead_of_falling_back(db_session, monkeypatch):
    monkeypatch.setattr("app.routers.auth._record_failed_login", lambda username: None)

    try:
        _login(db_session, "unknown-user", "admin123")
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "Incorrect username or password"
    else:
        raise AssertionError("Unknown users must not receive a fallback user's token")


def test_login_rejects_when_no_users_exist(db_session, monkeypatch):
    db_session.query(User).delete(synchronize_session=False)
    db_session.commit()
    monkeypatch.setattr("app.routers.auth._record_failed_login", lambda username: None)

    try:
        _login(db_session, "missing-user", "password")
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "Incorrect username or password"
    else:
        raise AssertionError("Login must fail when the database has no users")
