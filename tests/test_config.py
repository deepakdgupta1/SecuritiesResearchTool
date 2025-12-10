"""Unit tests for core configuration module.

Tests the Pydantic settings model and environment variable loading.
"""

import pytest
from pydantic import ValidationError

from backend.core.config import Settings


class TestSettings:
    """Test suite for Settings configuration."""

    def test_settings_with_all_required_fields(self, monkeypatch):
        """Test that Settings loads correctly with all required fields."""
        # Set required environment variables
        monkeypatch.setenv(
            "DATABASE_URL",
            "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("ZERODHA_API_KEY", "test_api_key")
        monkeypatch.setenv("ZERODHA_ACCESS_TOKEN", "test_access_token")

        # Create settings instance
        settings = Settings()

        # Verify required fields
        assert settings.DATABASE_URL == "postgresql://user:pass@localhost/testdb"
        assert settings.ZERODHA_API_KEY == "test_api_key"
        assert settings.ZERODHA_ACCESS_TOKEN == "test_access_token"

    def test_settings_with_defaults(self, monkeypatch):
        """Test that Settings applies default values correctly."""
        monkeypatch.setenv(
            "DATABASE_URL",
            "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("ZERODHA_API_KEY", "test_api_key")
        monkeypatch.setenv("ZERODHA_ACCESS_TOKEN", "test_access_token")

        settings = Settings()

        # Verify default values (note: conftest.py sets LOG_LEVEL=DEBUG in test
        # env)
        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.ENVIRONMENT == "testing"  # Set by conftest.py
        assert settings.BATCH_SIZE == 100
        assert settings.MAX_RETRIES == 3
        assert settings.HISTORICAL_YEARS == 20

    def test_settings_with_custom_values(self, monkeypatch):
        """Test that Settings accepts custom values for optional fields."""
        monkeypatch.setenv(
            "DATABASE_URL",
            "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("ZERODHA_API_KEY", "test_api_key")
        monkeypatch.setenv("ZERODHA_ACCESS_TOKEN", "test_access_token")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("BATCH_SIZE", "500")

        settings = Settings()

        assert settings.LOG_LEVEL == "DEBUG"
        assert settings.ENVIRONMENT == "production"
        assert settings.BATCH_SIZE == 500

    def test_settings_missing_required_field_raises_error(self, monkeypatch):
        """Test that missing required fields raise ValidationError."""
        # Remove required fields using monkeypatch
        # Need to remove DATABASE_URL too since Pydantic reads from .env file
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("ZERODHA_API_KEY", raising=False)
        monkeypatch.delenv("ZERODHA_ACCESS_TOKEN", raising=False)

        # Should raise ValidationError for missing required fields
        # Pass _env_file=None to prevent reading from .env file
        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_settings_invalid_log_level_raises_error(self, monkeypatch):
        """Test that invalid LOG_LEVEL raises ValidationError."""
        monkeypatch.setenv(
            "DATABASE_URL",
            "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("ZERODHA_API_KEY", "test_api_key")
        monkeypatch.setenv("ZERODHA_ACCESS_TOKEN", "test_access_token")
        monkeypatch.setenv("LOG_LEVEL", "INVALID")

        with pytest.raises(ValidationError):
            Settings()

    def test_settings_invalid_environment_raises_error(self, monkeypatch):
        """Test that invalid ENVIRONMENT raises ValidationError."""
        monkeypatch.setenv(
            "DATABASE_URL",
            "postgresql://user:pass@localhost/testdb")
        monkeypatch.setenv("ZERODHA_API_KEY", "test_api_key")
        monkeypatch.setenv("ZERODHA_ACCESS_TOKEN", "test_access_token")
        monkeypatch.setenv("ENVIRONMENT", "invalid_env")

        with pytest.raises(ValidationError):
            Settings()
