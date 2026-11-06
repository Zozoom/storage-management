from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    secret_key: str
    access_token_expire_minutes: int = 15
    cors_origins: str = "http://localhost:3000"

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: str) -> str:
        if value in {"dev-secret-change-me-in-production", "docker-dev-secret"}:
            raise ValueError("SECRET_KEY must not be a development value")
        if len(value) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters; use a randomly generated secret")
        return value


settings = Settings()
