"""Application configuration using Pydantic settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/trading_sim"

    # Application
    APP_NAME: str = "IDX Trading Simulator"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # yfinance
    YFINANCE_DELAY: float = 0.5  # Seconds between requests
    YFINANCE_RETRIES: int = 3
    YFINANCE_CACHE_DIR: str = "/tmp/yfinance"

    # Timezone
    TIMEZONE: str = "Asia/Jakarta"  # WIB (UTC+7)

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
