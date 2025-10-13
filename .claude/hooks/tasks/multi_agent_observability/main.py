#!/usr/bin/env python3
"""
Multi-Agent Observability Task - Sends Claude Code hook events to observability server.

This task:
1. Prepares event data with session ID, hook type, and payload
2. Optionally generates an LLM summary of the event
3. Optionally includes chat transcript from the session
4. Sends the event to the observability server via HTTP POST

Configuration (from hooks_config.yaml):
    source_app: Source application name (default: claude-code)
    server_host: IP address or hostname for the observability server (default: localhost)
    server_port: Port number for the observability server (default: 4000)
    add_chat: Whether to include chat transcript (boolean)
    summarize: Whether to generate an LLM summary (boolean)
    message_pattern: Jinja2 template file for summary prompt (required if summarize is true)
    llm:
        provider: LLM provider (openai, anthropic, ollama, tabby)
        model: Model identifier
        base_url: Base URL for API (optional, for local providers)
"""

import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional
from pyprojroot import here
from jinja2 import Environment, FileSystemLoader, TemplateNotFound


def _load_and_render_pattern(
    pattern_name: str, event_type: str, payload_str: str
) -> str:
    """
    Load a Jinja2 pattern template and render it with event data.

    Args:
        pattern_name: Name of the pattern file (e.g., "event_summary.j2")
        event_type: The hook event type
        payload_str: JSON string representation of the payload

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
    rendered = template.render(event_type=event_type, payload_str=payload_str)

    return rendered


def _call_llm_cli(
    provider: str,
    model: Optional[str],
    prompt: str,
    base_url: Optional[str] = None,
    timeout: int = 10,
) -> Optional[str]:
    """
    Call the LLM CLI to generate a summary.

    Args:
        provider: LLM provider (openai, anthropic, ollama, tabby)
        model: Model identifier (required for openai/anthropic/ollama)
        prompt: The prompt text (rendered pattern)
        base_url: Base URL for API (optional, for tabby/ollama)
        timeout: Subprocess timeout in seconds

    Returns:
        Generated summary text, or None if error
    """
    import subprocess

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


def _send_event_to_server(
    event_data: Dict[str, Any], server_host: str, server_port: int, timeout: int = 5
) -> bool:
    """
    Send event data to the observability server via HTTP POST.

    Args:
        event_data: The event data to send
        server_host: Hostname or IP address for the server
        server_port: Port number for the server
        timeout: Request timeout in seconds

    Returns:
        True if successful, False otherwise
    """
    server_url = f"http://{server_host}:{server_port}/events"

    try:
        # Prepare the request
        req = urllib.request.Request(
            server_url,
            data=json.dumps(event_data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Claude-Code-Hook/1.0",
            },
        )

        # Send the request
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status == 200

    except (urllib.error.URLError, urllib.error.HTTPError, Exception):
        return False


def send_event(
    input_data: Dict[str, Any],
    global_config: Dict[str, Any],
    source_app: str = "claude-code",
    server_host: str = "localhost",
    server_port: int = 4000,
    add_chat: bool = False,
    summarize: bool = False,
    message_pattern: Optional[str] = None,
    llm: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Send a Claude Code hook event to the observability server.

    This is the main entry point called by hook_entry.py. It orchestrates:
    1. Preparing event data with session ID, hook type, and payload
    2. Optionally generating an LLM summary
    3. Optionally including chat transcript
    4. Sending the event to the observability server

    Args:
        input_data: The input data received by the hook
        global_config: Global configuration settings
        source_app: Source application name
        server_host: Hostname or IP address for the observability server
        server_port: Port number for the observability server
        add_chat: Whether to include chat transcript
        summarize: Whether to generate an LLM summary
        message_pattern: Jinja2 template file for summary prompt
        llm: LLM configuration dict with keys: provider, model, base_url

    Returns:
        Optional dict with systemMessage if verbose logging is enabled
    """
    try:
        # Get timeout and logging settings from global config
        timeout = global_config.get("subprocess_timeout", 10)
        verbose_logging = global_config.get("verbose_logging", False)
        show_errors = global_config.get("show_errors", False)

        # Extract event type from input_data
        event_type = input_data.get("hook_event_name", "unknown")

        # Prepare event data for server
        event_data = {
            "source_app": source_app,
            "session_id": input_data.get("session_id", "unknown"),
            "hook_event_type": event_type,
            "payload": input_data,
            "timestamp": int(datetime.now().timestamp() * 1000),
        }

        # Handle add_chat option
        if add_chat and "transcript_path" in input_data:
            transcript_path = input_data["transcript_path"]
            if os.path.exists(transcript_path):
                # Read .jsonl file and convert to JSON array
                chat_data = []
                try:
                    with open(transcript_path, "r") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    chat_data.append(json.loads(line))
                                except json.JSONDecodeError:
                                    pass  # Skip invalid lines

                    # Add chat to event data
                    event_data["chat"] = chat_data
                except Exception:
                    pass  # Fail silently on chat read errors

        # Generate summary if requested
        if summarize:
            if not llm:
                if verbose_logging or show_errors:
                    return {
                        "systemMessage": "Multi-agent observability error: summarize enabled but no LLM configuration provided"
                    }
            elif not message_pattern:
                if verbose_logging or show_errors:
                    return {
                        "systemMessage": "Multi-agent observability error: summarize enabled but no message_pattern provided"
                    }
            else:
                try:
                    # Convert payload to formatted JSON string
                    payload_str = json.dumps(input_data, indent=2)

                    # Load and render the summary prompt pattern
                    pattern_prompt = _load_and_render_pattern(
                        message_pattern, event_type, payload_str
                    )

                    # Call LLM CLI to generate the summary
                    llm_provider = llm.get("provider", "anthropic")
                    llm_model = llm.get("model")
                    llm_base_url = llm.get("base_url")

                    summary = _call_llm_cli(
                        provider=llm_provider,
                        model=llm_model,
                        prompt=pattern_prompt,
                        base_url=llm_base_url,
                        timeout=timeout,
                    )

                    if summary:
                        event_data["summary"] = summary

                except (FileNotFoundError, Exception):
                    # Continue without summary if there's an error
                    pass

        # Send to server
        success = _send_event_to_server(event_data, server_host, server_port, timeout=5)

        if not success and (verbose_logging or show_errors):
            return {
                "systemMessage": f"Multi-agent observability: Failed to send event to server at {server_host}:{server_port}"
            }

        if verbose_logging:
            summary_text = f" with summary: {event_data.get('summary', 'none')[:50]}" if summarize else ""
            return {
                "systemMessage": f"Multi-agent observability: Event sent successfully{summary_text}"
            }

        return None

    except Exception as e:
        # Fail silently for any other errors (fail-open approach)
        if global_config.get("show_errors", True):
            return {"systemMessage": f"Multi-agent observability error: {e}"}
        return None
