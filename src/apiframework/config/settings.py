# /src/apiframework/config/settings.py
import os
from functools import lru_cache

from pydantic import Field, HttpUrl, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration, loaded from environment or .env."""

    model_config = SettingsConfigDict(
        env_prefix="BOOKER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    base_url: HttpUrl = Field(
        default=HttpUrl("https://restful-booker.herokuapp.com"),
        description="Base URL for the REST API",
    )
    username: str = Field(default="admin", description="Auth Username for the REST API")
    password: str = Field(default="password123", description="Auth Password for the REST API")
    timeout_seconds: float = Field(default=10.0, gt=0, le=60)

    @model_validator(mode="after")
    def _reject_unknown_prefixed_env_vars(self) -> "Settings":
        prefix = type(self).model_config["env_prefix"].upper()
        known = {f"{prefix}{name}".upper() for name in type(self).model_fields}
        unknown = sorted(
            key for key in os.environ if key.upper().startswith(prefix) and key.upper() not in known
        )
        if unknown:
            raise ValueError(
                f"Unrecognized {prefix}* environment variables: {unknown}. Known: {sorted(known)}"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so config is parsed once per process."""
    return Settings()
