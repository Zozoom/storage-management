import pytest
from fastapi import HTTPException

from app.models import Item, User
from app.routers.auth import _login


def test_login_with_empty_user_table_returns_unauthorized(db_session, monkeypatch):
    db_session.query(Item).delete(synchronize_session=False)
    db_session.query(User).delete(synchronize_session=False)
    db_session.commit()
    monkeypatch.setattr("app.routers.auth._record_failed_login", lambda username: None)

    with pytest.raises(HTTPException) as exc_info:
        _login(db_session, "missing-user", "password")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect username or password"
