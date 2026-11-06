from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.config import settings


def test_password_hash_verifies_original_and_rejects_incorrect_password():
    hashed_password = hash_password("correct-password")

    assert hashed_password != "correct-password"
    assert verify_password("correct-password", hashed_password)
    assert not verify_password("incorrect-password", hashed_password)


def test_created_token_contains_subject_and_expected_expiration():
    before_creation = datetime.now(timezone.utc)
    token = create_access_token("admin")
    after_creation = datetime.now(timezone.utc)

    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    expiration = datetime.fromtimestamp(payload["exp"], timezone.utc)
    expected_expiration = timedelta(minutes=settings.access_token_expire_minutes)

    assert payload["sub"] == "admin"
    assert before_creation + expected_expiration - timedelta(seconds=1) <= expiration
    assert expiration <= after_creation + expected_expiration + timedelta(seconds=1)


def test_current_user_resolves_valid_token(db_session):
    user = get_current_user(create_access_token("admin"), db_session)

    assert user.username == "admin"


@pytest.mark.parametrize("token_kind", ["expired", "malformed", "missing_subject", "unknown_user"])
def test_current_user_rejects_invalid_tokens(db_session, token_kind):
    if token_kind == "expired":
        token = jwt.encode(
            {
                "sub": "admin",
                "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
            },
            settings.secret_key,
            algorithm="HS256",
        )
    elif token_kind == "malformed":
        token = "not.a.valid-token"
    elif token_kind == "missing_subject":
        token = jwt.encode(
            {"exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
            settings.secret_key,
            algorithm="HS256",
        )
    else:
        token = create_access_token("unknown-user")

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(token, db_session)

    assert exc_info.value.status_code == 401
