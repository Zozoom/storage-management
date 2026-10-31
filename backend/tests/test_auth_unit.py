from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.config import settings
from app.models import User
from app.routers.auth import _login


def _signed_token(payload: dict, secret: str = settings.secret_key) -> str:
    return jwt.encode(payload, secret, algorithm="HS256")


def test_password_hashing_verifies_correct_and_incorrect_passwords():
    hashed_password = hash_password("correct-password")

    assert hashed_password != "correct-password"
    assert verify_password("correct-password", hashed_password)
    assert not verify_password("incorrect-password", hashed_password)


def test_login_requires_matching_password(db_session):
    token = _login(db_session, "admin", "admin123")
    assert jwt.decode(token.access_token, settings.secret_key, algorithms=["HS256"])["sub"] == "admin"

    with pytest.raises(HTTPException) as exc_info:
        _login(db_session, "admin", "wrong-password")

    assert exc_info.value.status_code == 401


def test_login_rejects_unknown_username(db_session):
    with pytest.raises(HTTPException) as exc_info:
        _login(db_session, "unknown-user", "admin123")

    assert exc_info.value.status_code == 401


def test_login_rejects_when_user_table_is_empty(db_session):
    db_session.query(User).delete()
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        _login(db_session, "admin", "admin123")

    assert exc_info.value.status_code == 401


def test_created_token_validates_and_loads_current_user(db_session):
    token = create_access_token("admin")

    assert jwt.decode(token, settings.secret_key, algorithms=["HS256"])["sub"] == "admin"
    assert get_current_user(token, db_session).username == "admin"


def test_get_current_user_rejects_invalid_tokens(db_session):
    valid_expiration = datetime.now(timezone.utc) + timedelta(minutes=5)
    expired_token = _signed_token(
        {"sub": "admin", "exp": datetime.now(timezone.utc) - timedelta(minutes=5)}
    )
    wrong_signature_token = _signed_token(
        {"sub": "admin", "exp": valid_expiration}, secret="wrong-secret"
    )
    missing_subject_token = _signed_token({"exp": valid_expiration})
    unknown_user_token = _signed_token(
        {"sub": "unknown-user", "exp": valid_expiration}
    )

    for token in (
        expired_token,
        "not-a-jwt",
        wrong_signature_token,
        missing_subject_token,
        unknown_user_token,
    ):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token, db_session)

        assert exc_info.value.status_code == 401
