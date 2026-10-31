from app.config import Settings


def test_default_access_token_expiry_is_short_lived(monkeypatch):
    monkeypatch.delenv("ACCESS_TOKEN_EXPIRE_MINUTES", raising=False)

    settings = Settings(
        _env_file=None,
        secret_key="a-unique-random-test-key-with-at-least-32-chars",
    )

    assert settings.access_token_expire_minutes == 15
