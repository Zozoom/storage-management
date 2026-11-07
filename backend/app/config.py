from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    environment: str = "development"
    secret_key: str = "dev-secret-change-me-in-production"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:3000"

    @model_validator(mode="after")
    def validate_production_secret(self):
        if self.environment.strip().lower() in {"production", "prod"}:
            if (
                self.secret_key in {
                    "dev-secret-change-me-in-production",
                    "docker-dev-secret",
                }
                or len(self.secret_key) < 32
            ):
                raise ValueError(
                    "Production requires a randomly generated SECRET_KEY "
                    "of at least 32 characters"
                )
        return self


settings = Settings()

