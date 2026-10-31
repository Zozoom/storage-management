from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth import get_current_user, hash_password
from app.config import settings


def test_password_verification_accepts_original_and_rejects_different_password():
    hashed_password = hash_password("correct-password")

    assert hashed_password != "correct-password"
    assert get_current_user is not None
    from app.auth import verify_password

    assert verify_password("correct-password", hashed_password) is True
    assert verify_password("different-password", hashed_password) is False


@pytest.mark.parametrize(
    "token",
    [
        "not-a-jwt",
        jwt.encode(
            {
                "sub": "admin",
                "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            },
            settings.secret_key,
            algorithm="HS256",
        ),
        jwt.encode(
            {
                "sub": "admin",
                "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
            },
            "a-different-signing-key-that-is-long-enough",
            algorithm="HS256",
        ),
        jwt.encode(
            {"exp": datetime.now(timezone.utc) + timedelta(minutes=1)},
            settings.secret_key,
            algorithm="HS256",
        ),
    ],
    ids=["malformed", "expired", "wrong-signature", "missing-subject"],
)
def test_get_current_user_rejects_invalid_tokens(db_session, token):
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)

    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_token_for_unknown_user(db_session):
    token = jwt.encode(
        {
            "sub": "unknown-user",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
        },
        settings.secret_key,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)

    assert exc_info.value.status_code == 401
