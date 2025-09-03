#!/usr/bin/env python3
"""
Shared configuration utilities for Claude Code hooks.

This module provides a centralized way for all hook scripts to load and access
configuration settings from hooks_config.yaml.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_hook_config(hook_name: str) -> Dict[str, Any]:
    """
    Load configuration for a specific hook from hooks_config.yaml.

    Args:
        hook_name: Name of the hook section to load (e.g., 'post_tool_use', 'stop')

    Returns:
        Dictionary containing the hook's configuration, or empty dict if not found

    Example:
        config = load_hook_config('post_tool_use')
        if config.get('log_to_file', True):
            # Log to file
    """
    try:
        config_path = Path(__file__).parent.parent / "config" / "hooks_config.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)
                return config_data.get(hook_name, {})
    except Exception:
        # If config loading fails, return empty dict to use defaults
        pass
    return {}


def load_global_config() -> Dict[str, Any]:
    """
    Load global configuration settings from hooks_config.yaml.

    Returns:
        Dictionary containing global configuration settings
    """
    try:
        config_path = Path(__file__).parent.parent / "config" / "hooks_config.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)
                return config_data.get("global", {})
    except Exception:
        pass
    return {}


def get_log_directory() -> Path:
    """
    Get the configured log directory path.

    Returns:
        Path object pointing to the log directory
    """
    global_config = load_global_config()
    log_dir_name = global_config.get("log_directory", "logs")
    return Path.cwd() / log_dir_name


def should_log_to_file(hook_name: str, default: bool = True) -> bool:
    """
    Check if a hook should log to file based on its configuration.

    Args:
        hook_name: Name of the hook
        default: Default value if not specified in config

    Returns:
        True if should log to file, False otherwise
    """
    hook_config = load_hook_config(hook_name)
    return hook_config.get("log_to_file", default)


def get_subprocess_timeout() -> int:
    """
    Get the configured subprocess timeout from global settings.

    Returns:
        Timeout in seconds (defaults to 10)
    """
    global_config = load_global_config()
    return global_config.get("subprocess_timeout", 10)


def get_agent_name(session_id: str = "") -> str:
    """
    Get the agent name for the current session.

    Args:
        session_id: The session ID to look up the agent name for

    Returns:
        Agent name in uppercase (defaults to "CLAUDE" if not found)
    """
    if not session_id:
        return "CLAUDE"

    try:
        # Load session data to get agent name
        sessions_dir = Path(".claude/data/sessions")
        session_file = sessions_dir / f"{session_id}.json"

        if session_file.exists():
            with open(session_file, "r") as f:
                session_data = json.load(f)
                if "agent_name" in session_data:
                    return session_data["agent_name"]
    except Exception:
        # Return default if anything goes wrong
        pass

    return "CLAUDE"
