"""Configuration settings for the Securities Research Tool.

This module loads and validates all configuration from environment variables
using Pydantic Settings for type safety and validation.

Usage:
    from backend.core.config import settings

    database_url = settings.DATABASE_URL
    api_key = settings.ZERODHA_API_KEY
"""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings are loaded from .env file or environment variables.
    Required settings will raise validation error if missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ==============================================================================
    # Database Configuration
    # ==============================================================================

    DATABASE_URL: str
    """PostgreSQL connection string (required)."""

    # ==============================================================================
    # Zerodha API Credentials
    # ==============================================================================

    ZERODHA_API_KEY: str
    """Zerodha API key (required)."""

    ZERODHA_ACCESS_TOKEN: str
    """Zerodha access token (required)."""

    # ==============================================================================
    # Application Settings
    # ==============================================================================

    LOG_LEVEL: Literal["DEBUG", "INFO",
                       "WARNING", "ERROR", "CRITICAL"] = "INFO"
    """Logging level."""

    ENVIRONMENT: Literal["development",
                         "testing", "production"] = "development"
    """Application environment."""

    # ==============================================================================
    # Data Loading Configuration
    # ==============================================================================

    BATCH_SIZE: int = 100
    """Number of rows to insert per database transaction."""

    MAX_RETRIES: int = 3
    """Maximum retry attempts for API calls."""

    RETRY_DELAY_SECONDS: int = 60
    """Initial retry delay in seconds (exponential backoff)."""

    HISTORICAL_YEARS: int = 20
    """Number of years of historical data to load."""

    # ==============================================================================
    # Rate Limiting
    # ==============================================================================

    ZERODHA_RATE_LIMIT: int = 3
    """Maximum requests per second to Zerodha API."""

    YAHOO_RATE_LIMIT: int = 10
    """Maximum requests per second to Yahoo Finance."""


# Global settings instance
settings = Settings()
"""Global settings instance - import this from other modules."""
