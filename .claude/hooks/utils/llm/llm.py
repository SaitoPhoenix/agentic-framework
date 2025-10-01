"""
Unified LLM Interface using PydanticAI - Supports multiple LLM providers with a consistent API.

This module provides a single function to interact with various LLM providers:
- Anthropic (Claude models)
- OpenAI (GPT models)
- Ollama (local models)
- TabbyAPI (local OpenAI-compatible API)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Type
from pydantic_ai import Agent
from pydantic_ai.models import Model as BaseModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers import Provider as BaseProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from .llm_config import get_provider_details


class Provider(str, Enum):
    ANTHROPIC = "ANTHROPIC"
    OPENAI = "OPENAI"
    OLLAMA = "OLLAMA"
    TABBY = "TABBY"


@dataclass(frozen=True)
class LLMConfig:
    model_class: Type[BaseModel]
    provider_class: Type[BaseProvider]


PROVIDER_CONFIGS: dict[Provider, LLMConfig] = {
    Provider.ANTHROPIC: LLMConfig(
        model_class=AnthropicModel, provider_class=AnthropicProvider
    ),
    Provider.OPENAI: LLMConfig(
        model_class=OpenAIChatModel, provider_class=OpenAIProvider
    ),
    Provider.OLLAMA: LLMConfig(
        model_class=OpenAIChatModel, provider_class=OpenAIProvider
    ),
    Provider.TABBY: LLMConfig(
        model_class=OpenAIChatModel, provider_class=OpenAIProvider
    ),
}


async def prompt_llm(
    provider: Provider,
    model: str,
    prompt: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Optional[str]:
    """
    Prompt an LLM provider with a unified interface using PydanticAI.

    Args:
        provider: Provider name ("ANTHROPIC", "OPENAI", "OLLAMA", "TABBY")
        model: Model identifier (e.g., "claude-3-5-haiku-latest", "gpt-4o-mini", "gpt-oss:20b")
        prompt: The prompt text to send to the model
        base_url: Base URL for the API (optional, used for local/custom endpoints)
        api_key: API key (optional, will use env vars if not provided)

    Returns:
        str: The model's response text, or None if error

    Examples:
        >>> # Anthropic
        >>> prompt_llm("ANTHROPIC", "claude-3-5-haiku-latest", "Hello!")

        >>> # OpenAI
        >>> prompt_llm("OPENAI", "gpt-4o-mini", "Hello!")

        >>> # Ollama (local)
        >>> prompt_llm("OLLAMA", "gpt-oss:20b", "Hello!", base_url="http://localhost:11434/v1")

        >>> # TabbyAPI (local)
        >>> prompt_llm("TABBY", "my-model", "Hello!", base_url="http://localhost:5000/v1")
    """
    provider = provider.upper()

    try:
        # Create the appropriate model based on provider
        model_instance = _create_model(provider, model, base_url, api_key)
        agent = Agent(model=model_instance)
        result = await agent.run(prompt)
        return result.output

    except Exception as e:
        print(f"Error during LLM Call: {e}")
        return None


def _create_model(
    provider: Provider,
    llm_model: str,
    base_url: Optional[str],
    api_key: Optional[str],
):
    config = PROVIDER_CONFIGS.get(provider)
    if not config:
        raise ValueError(f"Unsupported provider: '{provider.value}'")
    # Get provider details from config if not provided
    provider_details = get_provider_details(provider)
    final_api_key = api_key or provider_details.api_key
    final_base_url = base_url or provider_details.base_url
    if not final_api_key:
        raise ValueError(f"API key for provider '{provider}' is missing.")

    provider_instance = config.provider_class(
        api_key=final_api_key, base_url=final_base_url
    )

    return config.model_class(
        model_name=llm_model,
        provider=provider_instance,
    )
