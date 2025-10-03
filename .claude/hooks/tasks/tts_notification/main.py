#!/usr/bin/env python3
"""
TTS Notification Task - Announces completion messages using LLM-generated text and TTS.

This task:
1. Loads a Jinja2 pattern template for message generation
2. Calls the LLM CLI to generate a personalized completion message
3. Calls the TTS CLI to play the generated message as audio

Configuration (from hooks_config.yaml):
    tts:
        provider: TTS provider (openai, gcloud, elevenlabs, pyttsx3)
        voice: Voice identifier for the TTS provider
        model: Model identifier (openai/elevenlabs only)
    llm:
        provider: LLM provider (openai, anthropic, ollama, tabby)
        model: Model identifier
        base_url: Base URL for API (optional, for local providers)
    llm_message_pattern: Path to Jinja2 template file (relative to patterns directory)
    user_name: User's name for personalization (optional)
"""

import subprocess
import sys
from typing import Dict, Any, Optional
from pyprojroot import here
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


def _load_and_render_pattern(pattern_name: str, user_name: Optional[str] = None) -> str:
    """
    Load a Jinja2 pattern template and render it with provided variables.

    Args:
        pattern_name: Name of the pattern file (e.g., "completion_message.j2")
        user_name: Optional user name for personalization

    Returns:
        Rendered pattern text ready to be sent to LLM

    Raises:
        FileNotFoundError: If pattern file doesn't exist
    """
    patterns_dir = here() / ".claude" / "hooks" / "utils" / "patterns"

    # Create Jinja2 environment with the patterns directory
    env = Environment(loader=FileSystemLoader(str(patterns_dir)))

    try:
        template = env.get_template(pattern_name)
    except TemplateNotFound:
        raise FileNotFoundError(
            f"Pattern file not found: {patterns_dir / pattern_name}"
        )

    # Render template with variables
    rendered = template.render(user_name=user_name)

    return rendered


def _call_llm_cli(
    provider: str,
    model: Optional[str],
    prompt: str,
    base_url: Optional[str] = None,
    timeout: int = 10,
) -> Optional[str]:
    """
    Call the LLM CLI to generate a completion message.

    Args:
        provider: LLM provider (openai, anthropic, ollama, tabby)
        model: Model identifier (required for openai/anthropic/ollama)
        prompt: The prompt text (rendered pattern)
        base_url: Base URL for API (optional, for tabby/ollama)
        timeout: Subprocess timeout in seconds

    Returns:
        Generated message text, or None if error
    """
    llm_cli_path = here() / ".claude" / "hooks" / "utils" / "llm" / "llm_cli.py"

    if not llm_cli_path.exists():
        return None

    # Build the command
    cmd = ["uv", "run", str(llm_cli_path), provider]

    # Add model (required for most providers, use a default if None)
    if model:
        cmd.append(model)
    else:
        # Default models for providers that don't specify
        default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-latest",
            "ollama": "gpt-oss:20b",
            "tabby": "tabby-default",
        }
        cmd.append(default_models.get(provider.lower(), "default"))

    # Add prompt
    cmd.append(prompt)

    # Add optional base_url (only if not None and not empty string)
    if base_url and base_url.strip():
        cmd.extend(["--base-url", base_url])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode == 0:
            # In non-verbose mode, CLI outputs only the message
            return result.stdout.strip()

        return None

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return None


def _call_tts_cli(
    provider: str,
    voice: Optional[str],
    model: Optional[str],
    text: str,
    timeout: int = 10,
) -> bool:
    """
    Call the TTS CLI to play the generated message as audio.

    Args:
        provider: TTS provider (pyttsx3, openai, gcloud, elevenlabs)
        voice: Voice identifier for the TTS provider
        model: Model identifier (openai/elevenlabs only)
        text: The text to synthesize and play
        timeout: Subprocess timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    tts_cli_path = here() / ".claude" / "hooks" / "utils" / "tts" / "tts-cli.py"

    if not tts_cli_path.exists():
        return False

    # Build the command
    cmd = ["uv", "run", str(tts_cli_path), "--provider", provider]

    # Add voice if provided
    if voice:
        cmd.extend(["--voice", voice])

    # Add model if provided (only for openai/elevenlabs)
    if model and provider.lower() in ["openai", "elevenlabs"]:
        cmd.extend(["--model", model])

    # Add text
    cmd.append(text)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
        )

        return result.returncode == 0

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        return False


def announce_tts(
    input_data: Dict[str, Any],
    global_config: Dict[str, Any],
    tts: Optional[Dict[str, Any]] = None,
    llm: Optional[Dict[str, Any]] = None,
    message_pattern: str = "completion_message.j2",
    user_name: Optional[str] = None,
    **kwargs,
) -> None:
    """
    Announce a completion message using LLM-generated text and TTS.

    This is the main entry point called by hook_entry.py. It orchestrates:
    1. Loading and rendering the message pattern
    2. Generating a completion message via LLM CLI
    3. Playing the message via TTS CLI

    Args:
        input_data: The input data received by the hook (unused)
        global_config: Global configuration settings
        tts: TTS configuration dict with keys: provider, voice, model
        llm: LLM configuration dict with keys: provider, model, base_url
        message_pattern: Name of Jinja2 pattern file
        user_name: User's name for personalization
        **kwargs: Additional configuration parameters (unused)
    """
    try:
        # Get timeout from global config
        timeout = global_config.get("subprocess_timeout", 10)
        verbose_errors = global_config.get("verbose_errors", False)

        # Validate required configurations
        if not tts or not llm:
            if verbose_errors:
                print(
                    "TTS notification error: missing tts or llm configuration",
                    file=sys.stderr,
                )
            return

        # Step 1: Load and render the pattern template
        try:
            pattern_prompt = _load_and_render_pattern(message_pattern, user_name)
        except FileNotFoundError as e:
            if verbose_errors:
                print(f"TTS notification error: {e}", file=sys.stderr)
            return

        # Step 2: Call LLM CLI to generate the message
        llm_provider = llm.get("provider", "tabby")
        llm_model = llm.get("model")
        llm_base_url = llm.get("base_url")

        generated_message = _call_llm_cli(
            provider=llm_provider,
            model=llm_model,
            prompt=pattern_prompt,
            base_url=llm_base_url,
            timeout=timeout,
        )

        if not generated_message:
            if verbose_errors:
                print(
                    "TTS notification error: LLM CLI failed to generate message",
                    file=sys.stderr,
                )
            return

        # Step 3: Call TTS CLI to play the message
        tts_provider = tts.get("provider", "pyttsx3")
        tts_voice = tts.get("voice")
        tts_model = tts.get("model")

        success = _call_tts_cli(
            provider=tts_provider,
            voice=tts_voice,
            model=tts_model,
            text=generated_message,
            timeout=timeout,
        )

        if not success and verbose_errors:
            print(
                "TTS notification error: TTS CLI failed to play message",
                file=sys.stderr,
            )

    except Exception as e:
        # Fail silently for any other errors
        if global_config.get("verbose_errors", False):
            print(f"TTS notification error: {e}", file=sys.stderr)
