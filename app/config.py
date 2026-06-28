from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    gemini_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_webhook_url: str = ""
    email_host: str = ""
    email_port: int = 587
    email_username: str = Field(default="", validation_alias=AliasChoices("EMAIL_USERNAME", "SMTP_USER"))
    email_app_password: str = Field(
        default="",
        validation_alias=AliasChoices("EMAIL_APP_PASSWORD", "SMTP_PASSWORD"),
    )
    email_from: str = ""
    email_use_tls: bool = True

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
