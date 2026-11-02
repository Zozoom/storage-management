import pytest
from pydantic import ValidationError

from app.config import COMPOSE_DEV_SECRET, Settings


def test_secret_key_is_required_outside_tests(monkeypatch):
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.parametrize("secret", ["short", "a" * 40, "replace-with-a-random-secret-value"])
def test_rejects_weak_secret_keys(secret):
    with pytest.raises(ValidationError, match="SECRET_KEY must be"):
        Settings(_env_file=None, secret_key=secret)


def test_rejects_compose_development_secret_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    with pytest.raises(ValidationError, match="Compose development SECRET_KEY"):
        Settings(_env_file=None, secret_key=COMPOSE_DEV_SECRET)
