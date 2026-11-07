from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.config import settings
from app.models import Item, User
from app.seed import seed_db


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
    invalid_requests = [
        ("/api/auth/login/json", {"username": "admin", "password": "wrong"}, "json"),
        ("/api/auth/login/json", {"username": "unknown", "password": "wrong"}, "json"),
        ("/api/auth/login", {"username": "admin", "password": "wrong"}, "form"),
        ("/api/auth/login", {"username": "unknown", "password": "wrong"}, "form"),
    ]
    for endpoint, body, encoding in invalid_requests:
        response = client.post(endpoint, **{encoding: body})
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"


def test_me_requires_auth(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "admin"


def test_password_helpers():
    hashed = hash_password("correct-password")
    assert verify_password("correct-password", hashed)
    assert not verify_password("wrong-password", hashed)


def test_create_access_token_authenticates_its_subject(db_session):
    user = get_current_user(create_access_token("admin"), db_session)
    assert user.username == "admin"


def test_access_token_lifetime_is_capped(monkeypatch):
    monkeypatch.setattr(settings, "access_token_expire_minutes", 60)
    token = create_access_token("admin")
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    expiration = datetime.fromtimestamp(payload["exp"], timezone.utc)
    now = datetime.now(timezone.utc)

    assert now < expiration <= now + timedelta(minutes=15)


def test_seed_db_does_not_create_production_users_without_provisioning(
    db_session, monkeypatch
):
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.delenv("INITIAL_ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("INITIAL_ADMIN_PASSWORD", raising=False)
    db_session.query(Item).delete()
    db_session.query(User).delete()
    db_session.commit()

    seed_db(db_session)

    assert db_session.query(User).count() == 0
    items = db_session.query(Item).all()
    assert len(items) == 3
    assert all(item.created_by_id is None for item in items)


def test_get_current_user_rejects_invalid_tokens(db_session):
    invalid_tokens = [
        "not.a.valid.token",
        jwt.encode(
            {"sub": "admin", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
            settings.secret_key,
            algorithm="HS256",
        ),
        jwt.encode(
            {"exp": datetime.now(timezone.utc) + timedelta(minutes=1)},
            settings.secret_key,
            algorithm="HS256",
        ),
        create_access_token("unknown-user"),
    ]
    for token in invalid_tokens:
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token, db_session)
        assert exc_info.value.status_code == 401


def test_login_rate_limiter_applies_progressive_delays():
    from app.routers.auth import _LoginRateLimiter

    now = [0.0]
    limiter = _LoginRateLimiter(
        threshold=2,
        base_delay=1,
        max_delay=8,
        clock=lambda: now[0],
    )
    keys = [("account", "test-user"), ("ip", "127.0.0.1")]

    limiter.record_failure(keys)
    assert limiter.retry_after(keys) == 0

    limiter.record_failure(keys)
    assert limiter.retry_after(keys) == 1

    now[0] += 1
    assert limiter.retry_after(keys) == 0
    limiter.record_failure(keys)
    assert limiter.retry_after(keys) == 2
