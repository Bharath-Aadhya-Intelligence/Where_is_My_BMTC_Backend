"""
Application configuration using Pydantic Settings.
All configuration is loaded from environment variables / .env file.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Where Is My BMTC API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"

    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/"
    MONGODB_DB: str = "bmtc"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = True

    # CORS
    CORS_ORIGINS: str = "*"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Simulation
    SIMULATION_INTERVAL_SECONDS: float = 3.0
    SIMULATION_STEPS_BETWEEN_STOPS: int = 10

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
