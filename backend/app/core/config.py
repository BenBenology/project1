"""Configuration helpers loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings shared by backend and local development."""

    app_env: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    database_url: str = "sqlite:///./data/app.db"
    mock_task_delay_seconds: int = 2
    sec_user_agent: str = "project1 research app your-email@example.com"
    browser_user_agent: str = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cache settings so modules reuse one config instance."""
    return Settings()
