#!/usr/bin/env python3
"""
File Matcher - Gitignore-style pattern matching for file rules
"""

import pathspec
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from .shell_parser import extract_paths_from_command, normalize_path_with_quotes


def check_file_rules(
    tool_name: str,
    tool_input: Dict[str, Any],
    file_rules: List[Dict[str, Any]],
    permission_level: str,
) -> Optional[Tuple[str, str, str]]:
    """
    Check if a tool call matches any file blocking rules.

    Args:
        tool_name: Name of the tool being used
        tool_input: Input parameters for the tool
        file_rules: List of file rule dictionaries
        permission_level: "allow", "ask", or "deny"

    Returns:
        Tuple of (permission, message, matched_pattern) if match found, None otherwise
    """
    # Only check file-related tools
    if tool_name not in ["Read", "Edit", "MultiEdit", "Write", "Bash"]:
        return None

    # Get file path from tool input
    file_path = None

    if tool_name in ["Read", "Edit", "MultiEdit", "Write"]:
        file_path = tool_input.get("file_path", "")
    elif tool_name == "Bash":
        # Extract file paths from bash commands
        command = tool_input.get("command", "")
        file_path = extract_file_from_bash(command)

    if not file_path:
        return None

    # Normalize file path
    normalized_path = str(Path(file_path))

    # Check each rule
    for rule in file_rules:
        pattern = rule.get("pattern", "")
        rule_tools = rule.get("tools", [])
        message = rule.get("message", "")

        # Skip if tool-specific rule doesn't apply to this tool
        if rule_tools and tool_name not in rule_tools:
            continue

        # Check if pattern matches
        match_result = matches_file_pattern(normalized_path, pattern)

        if match_result:
            # Use custom message or default
            if not message:
                message = f"Sensitive file access prevented for safety: {pattern}"

            return (permission_level, message, pattern)

    return None


def matches_file_pattern(file_path: str, pattern: str) -> bool:
    """
    Check if a file path matches a gitignore-style pattern (case-insensitive).

    Args:
        file_path: File path to check
        pattern: Gitignore-style pattern (supports *, **, negation with !)

    Returns:
        True if pattern matches, False otherwise
    """
    # Handle negation patterns (whitelist) - these match when file DOES match the pattern after !
    is_negation = pattern.startswith("!")
    if is_negation:
        pattern = pattern[1:]  # Remove ! prefix

    # Normalize to lowercase for case-insensitive matching
    file_path_lower = file_path.lower()
    pattern_lower = pattern.lower()

    # Remember if pattern was originally a simple filename pattern (no path separators)
    is_filename_pattern = "/" not in pattern_lower and not pattern_lower.startswith("**")

    # Treat pattern as global if it doesn't start with / or contain /
    if is_filename_pattern:
        pattern_lower = f"**/{pattern_lower}"

    # Create pathspec matcher
    spec = pathspec.PathSpec.from_lines("gitwildmatch", [pattern_lower])

    # Check match on full path
    full_match = spec.match_file(file_path_lower)
    if full_match:
        return True

    # Also check if the filename ends with the pattern (for patterns without path separators)
    # This handles cases like "secrets.json" matching "my secrets.json"
    if is_filename_pattern:
        basename = Path(file_path_lower).name
        # Extract just the filename part from the original pattern (after **//)
        filename_pattern = pattern_lower.replace("**/", "")
        # Check if basename ends with the pattern
        if basename.endswith(filename_pattern):
            return True

    return False


def extract_file_from_bash(command: str) -> Optional[str]:
    """
    Extract file path from bash command for pattern matching.

    Handles quoted paths with spaces.

    Args:
        command: Bash command string

    Returns:
        Extracted file path or None
    """
    # Use shell parser to extract paths
    paths = extract_paths_from_command(command)

    if paths:
        # Return first path found, normalized to handle quotes
        return normalize_path_with_quotes(paths[0])

    return None
