from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    secret_key: str = "dev-secret-change-me-in-production"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = "http://localhost:3000"


settings = Settings()

