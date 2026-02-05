"""Application settings — loaded once at startup via pydantic-settings."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Edition(StrEnum):
    COMMUNITY = "community"
    ENTERPRISE = "enterprise"


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # ── Core ───────────────────────────────────────────────────────────
    edition: Edition = Edition.COMMUNITY
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/privai"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # ── Storage ────────────────────────────────────────────────────────
    storage_backend: str = "local"
    storage_local_root: Path = Path("./storage")

    @model_validator(mode="after")
    def validate_secrets(self) -> Settings:
        if self.jwt_secret == "change-me-in-production":
            import warnings

            warnings.warn(
                "JWT_SECRET is set to the default value — change it in production",
                UserWarning,
                stacklevel=1,
            )
        return self


settings = Settings()
