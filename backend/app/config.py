from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = 15
    cors_origins: str = "http://localhost:3000"


settings = Settings()

