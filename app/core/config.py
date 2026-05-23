"""
Application configuration using Pydantic Settings.
All configuration is loaded from environment variables / .env file.
"""

import os
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "Where Is My BMTC API"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def is_render(self) -> bool:
        return os.getenv("RENDER", "").lower() in ("true", "1", "yes")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production" or self.is_render

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @model_validator(mode="after")
    def apply_platform_defaults(self) -> "Settings":
        """Sensible defaults for Render and other PaaS hosts."""
        if self.is_render:
            # Render injects PORT; keep in sync for any code that reads settings.PORT
            render_port = os.getenv("PORT")
            if render_port:
                object.__setattr__(self, "PORT", int(render_port))

            # No local Redis unless a Render Redis URL was attached
            if self.REDIS_URL.startswith("redis://localhost") and not os.getenv(
                "REDIS_INTERNAL_URL"
            ):
                object.__setattr__(self, "REDIS_ENABLED", False)

        return self


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
