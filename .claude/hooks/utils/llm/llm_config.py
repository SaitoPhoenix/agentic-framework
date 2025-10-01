from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pyprojroot import here


class ApiSettings(BaseSettings):
    """
    Loads all known API keys from environment variables.
    Pydantic automatically matches class attributes to environment variables
    (case-insensitively).
    """

    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OLLAMA_API_KEY: Optional[str] = "ollama"
    OLLAMA_BASE_URL: Optional[str] = "http://localhost:11434/v1"
    TABBY_API_KEY: Optional[str] = "dummy"
    TABBY_BASE_URL: Optional[str] = "http://localhost:5000/v1"

    model_config = SettingsConfigDict(
        env_file=here() / ".env", env_file_encoding="utf-8", extra="ignore"
    )


class ProviderDetails(BaseModel):
    """A container for the validated settings for a specific provider."""

    api_key: Optional[str]
    base_url: Optional[str]


@lru_cache(maxsize=1)
def get_settings() -> ApiSettings:
    """
    Loads settings and caches the result so the .env file and environment
    are only read once.
    """
    return ApiSettings()


def get_provider_details(provider: str) -> ProviderDetails:
    """
    Retrieves the API key and base URL for a given provider.
    """
    settings = get_settings()

    # Dynamically build the attribute names and get them from the settings object
    api_key = getattr(settings, f"{provider}_API_KEY", None)
    base_url = getattr(settings, f"{provider}_BASE_URL", None)

    return ProviderDetails(api_key=api_key, base_url=base_url)
