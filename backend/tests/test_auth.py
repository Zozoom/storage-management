from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException
from jose import jwt
from pydantic import ValidationError

from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.config import Settings, settings
from app.models import User


def test_settings_require_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_reject_short_secret_key():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, secret_key="short")


def test_settings_reject_known_development_secret():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, secret_key="docker-dev-secret")


def test_access_token_lifetime_defaults_to_15_minutes():
    settings = Settings(_env_file=None, secret_key="test-only-secret-key-with-sufficient-length")
    assert settings.access_token_expire_minutes == 15


def test_password_hash_verifies_correct_password_and_rejects_incorrect_password():
    hashed_password = hash_password("correct-password")

    assert verify_password("correct-password", hashed_password)
    assert not verify_password("incorrect-password", hashed_password)


def test_access_token_contains_subject_and_future_expiration():
    token = create_access_token("admin")
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    expires_at = datetime.fromtimestamp(payload["exp"], timezone.utc)
    now = datetime.now(timezone.utc)

    assert payload["sub"] == "admin"
    assert expires_at > now
    assert expires_at <= now + timedelta(
        minutes=settings.access_token_expire_minutes, seconds=1
    )


def _encode_test_token(payload, secret_key=settings.secret_key):
    return jwt.encode(payload, secret_key, algorithm="HS256")


def test_get_current_user_rejects_invalid_signature(db_session):
    token = _encode_test_token(
        {
            "sub": "admin",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            "jti": uuid4().hex,
        },
        secret_key="different-test-secret-key-with-sufficient-length",
    )

    with pytest.raises(HTTPException) as error:
        get_current_user(token, db_session)

    assert error.value.status_code == 401


def test_get_current_user_rejects_expired_token(db_session):
    token = _encode_test_token(
        {
            "sub": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            "jti": uuid4().hex,
        }
    )

    with pytest.raises(HTTPException) as error:
        get_current_user(token, db_session)

    assert error.value.status_code == 401


def test_get_current_user_rejects_missing_subject(db_session):
    token = _encode_test_token(
        {
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
            "jti": uuid4().hex,
        }
    )

    with pytest.raises(HTTPException) as error:
        get_current_user(token, db_session)

    assert error.value.status_code == 401


def test_get_current_user_rejects_unknown_user(db_session):
    token = create_access_token("unknown-user")

    with pytest.raises(HTTPException) as error:
        get_current_user(token, db_session)

    assert error.value.status_code == 401


def test_login_success(client):
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_issues_token_for_requested_user(client, db_session):
    db_session.add(User(username="clerk", hashed_password=hash_password("clerk123")))
    db_session.commit()

    response = client.post(
        "/api/auth/login/json",
        json={"username": "clerk", "password": "clerk123"},
    )

    assert response.status_code == 200
    payload = jwt.decode(
        response.json()["access_token"], settings.secret_key, algorithms=["HS256"]
    )
    assert payload["sub"] == "clerk"


def test_login_rejects_invalid_credentials(client):
    invalid_credentials = (
        {"username": "admin", "password": "wrong"},
        {"username": "", "password": ""},
        {"username": "unknown", "password": "admin123"},
    )
    for credentials in invalid_credentials:
        response = client.post("/api/auth/login/json", json=credentials)
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"


def test_form_login_rejects_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_logout_revokes_access_token(client):
    login_response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_response = client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 204
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_me_requires_auth(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"
