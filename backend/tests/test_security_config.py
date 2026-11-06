import pytest
from pydantic import ValidationError

from app.config import Settings


@pytest.mark.parametrize(
    "secret_key",
    [
        "dev-secret-change-me-in-production",
        "docker-dev-secret",
        "short",
    ],
)
def test_settings_rejects_weak_or_known_development_secrets(secret_key):
    with pytest.raises(ValidationError):
        Settings(secret_key=secret_key)


def test_settings_accepts_a_long_random_secret():
    settings = Settings(secret_key="random-deployment-secret-" + "x" * 40)
    assert settings.secret_key == "random-deployment-secret-" + "x" * 40
