"""Application configuration.

Settings are read from environment variables (and from a local `.env` file
if present). Defaults here must be safe, non-secret values only — real
secrets belong in the environment, never in source code.
"""

from functools import lru_cache
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore unrelated variables in the environment
    )

    app_name: str = "ResumeIQ API"
    app_description: str = "AI-powered resume analysis platform"
    app_version: str = "0.1.0"
    environment: Literal["development", "testing", "production"] = "development"
    debug: bool = False

    # --- Database ---
    # SQLAlchemy URL using the psycopg 3 driver. The default has no
    # credentials and only works for a local, trust-authenticated PostgreSQL;
    # set DATABASE_URL in your environment or .env for anything else.
    database_url: str = "postgresql+psycopg://localhost:5432/resumeiq"
    # Log every SQL statement (useful while learning/debugging).
    db_echo: bool = False
    # Separate database used by the test suite. DB tests are skipped if unset.
    test_database_url: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (environment is read once)."""
    return Settings()
