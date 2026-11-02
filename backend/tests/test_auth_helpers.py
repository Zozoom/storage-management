from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt
from starlette.requests import Request

from app.auth import (
    SESSION_COOKIE,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.config import settings


def request_with_session(token: str) -> Request:
    return Request(
        {
            "type": "http",
            "headers": [(b"cookie", f"{SESSION_COOKIE}={token}".encode())],
        }
    )


def test_password_hash_accepts_original_and_rejects_different_password():
    hashed = hash_password("correct-password")

    assert verify_password("correct-password", hashed)
    assert not verify_password("different-password", hashed)


def test_access_token_contains_subject_and_expiry():
    token = create_access_token("admin")
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])

    assert payload["sub"] == "admin"
    assert datetime.fromtimestamp(payload["exp"], timezone.utc) > datetime.now(timezone.utc)


@pytest.mark.parametrize(
    "token",
    [
        jwt.encode(
            {"sub": "admin", "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
            settings.secret_key,
            algorithm="HS256",
        ),
        "not-a-jwt",
        jwt.encode(
            {"sub": "admin", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
            "incorrect-signing-key",
            algorithm="HS256",
        ),
    ],
    ids=["expired", "malformed", "incorrect-signature"],
)
def test_get_current_user_rejects_invalid_tokens(db_session, token):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(request_with_session(token), db_session)

    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_token_without_subject(db_session):
    token = jwt.encode(
        {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        settings.secret_key,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(request_with_session(token), db_session)

    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_subject_without_database_user(db_session):
    token = create_access_token("unknown-user")

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(request_with_session(token), db_session)

    assert exc_info.value.status_code == 401
