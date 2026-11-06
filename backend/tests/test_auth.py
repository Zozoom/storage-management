from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.config import settings


def test_login_success(client):
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_rejects_invalid_credentials(client):
    wrong_password = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "wrong"},
    )
    unknown_user = client.post(
        "/api/auth/login/json",
        json={"username": "unknown", "password": "admin123"},
    )
    form_login = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrong"},
    )

    for response in (wrong_password, unknown_user, form_login):
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"


def test_form_login_success(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_me_requires_auth(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_password_hash_verification():
    hashed = hash_password("correct-password")

    assert verify_password("correct-password", hashed)
    assert not verify_password("different-password", hashed)


def test_get_current_user_valid_token(db_session):
    user = get_current_user(create_access_token("admin"), db_session)

    assert user.username == "admin"


def test_get_current_user_rejects_invalid_tokens(db_session):
    expired_token = jwt.encode(
        {"sub": "admin", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm="HS256",
    )
    subjectless_token = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=1)},
        settings.secret_key,
        algorithm="HS256",
    )
    invalid_tokens = [
        "not-a-jwt",
        expired_token,
        subjectless_token,
        create_access_token("unknown-user"),
    ]

    for token in invalid_tokens:
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token, db_session)
        assert exc_info.value.status_code == 401


def test_get_current_user_rejects_revoked_token(db_session):
    from app.auth import revoke_access_token

    token = create_access_token("admin")
    revoke_access_token(token)

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)

    assert exc_info.value.status_code == 401


def test_login_rejects_when_user_table_is_empty(db_session):
    from app.routers.auth import _login
    from app.models import User

    db_session.query(User).delete()
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        _login(db_session, "admin", "admin123")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect username or password"
