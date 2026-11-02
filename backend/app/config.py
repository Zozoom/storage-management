import os
import secrets

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


COMPOSE_DEV_SECRET = "local-compose-only-insecure-secret"


def _is_production() -> bool:
    return any(
        os.getenv(name, "").strip().lower() == "production"
        for name in ("APP_ENV", "ENVIRONMENT", "VERCEL_ENV")
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    secret_key: str
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:3000"

    @model_validator(mode="before")
    @classmethod
    def provide_test_secret(cls, values: dict) -> dict:
        # Keep isolated tests self-contained without providing a deployment default.
        if (
            os.getenv("TESTING") == "1"
            and not values.get("secret_key")
            and not os.getenv("SECRET_KEY")
        ):
            values["secret_key"] = secrets.token_urlsafe(32)
        return values

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if value == COMPOSE_DEV_SECRET and not _is_production():
            return value
        if (
            len(value) < 32
            or len(set(value)) < 8
            or value != value.strip()
            or any(marker in value.lower() for marker in ("change-me", "replace-with", "password", "secret-key"))
        ):
            raise ValueError(
                "SECRET_KEY must be a unique, randomly generated value of at least 32 characters"
            )
        if _is_production() and value == COMPOSE_DEV_SECRET:
            raise ValueError("The Compose development SECRET_KEY cannot be used in production")
        return value


settings = Settings()
