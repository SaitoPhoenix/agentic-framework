#!/usr/bin/env python3
"""
Log Hook Task - Reusable logging function for any hook.

This module provides a generic logging function that can be used by any hook
to log input data to hook-specific JSON log files.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any
from pyprojroot import here


def log_hook_data(
    input_data: Dict[str, Any],
    global_config: Dict[str, Any],
    hook_name: str = None,
    **kwargs,
) -> None:
    """
    Log hook input data to a JSON file.

    Args:
        input_data: The input data received by the hook
        global_config: Global configuration settings
        hook_name: Name of the hook (used for log filename)
        **kwargs: Additional configuration parameters (unused, for compatibility)
    """
    try:
        # Determine hook name from input_data if not provided
        if not hook_name:
            # Try to infer from context or use a default
            hook_name = input_data.get("hook_event_name", "unknown_hook")

        # Get log directory from global config (always in project root)
        log_dir_name = global_config.get("log_directory", "logs")
        log_dir = here() / log_dir_name
        log_dir.mkdir(exist_ok=True)

        # Create hook-specific log file path
        log_path = log_dir / f"{hook_name}.json"

        # Read existing log data or initialize empty list
        if log_path.exists():
            try:
                with open(log_path, "r") as f:
                    log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
        else:
            log_data = []

        # Append new data
        log_data.append(input_data)

        # Write back to file with formatting
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)

    except Exception as e:
        # Fail silently unless verbose errors are enabled
        if global_config.get("verbose_errors", False):
            print(f"Log hook error: {e}", file=sys.stderr)
