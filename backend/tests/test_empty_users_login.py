import pytest
from fastapi import HTTPException

from app.models import Item, User
from app.routers.auth import _login


def test_login_with_empty_users_table_returns_unauthorized(db_session):
    db_session.query(Item).delete()
    db_session.query(User).delete()
    db_session.commit()

    with pytest.raises(HTTPException) as error:
        _login(db_session, "admin", "admin123")

    assert error.value.status_code == 401
    assert error.value.detail == "Incorrect username or password"
