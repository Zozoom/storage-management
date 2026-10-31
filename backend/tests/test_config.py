import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.mark.parametrize(
    "secret_key",
    [
        "dev-secret-change-me-in-production",
        "docker-dev-secret",
        "too-short",
    ],
)
def test_settings_reject_weak_or_development_secret_keys(secret_key):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, secret_key=secret_key)


def test_settings_require_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_accept_strong_secret_key():
    settings = Settings(
        _env_file=None,
        secret_key="a-unique-random-test-key-with-at-least-32-chars",
    )

    assert len(settings.secret_key) >= 32
