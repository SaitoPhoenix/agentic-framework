#!/usr/bin/env python3
"""
File Matcher - Gitignore-style pattern matching for file rules
"""

import pathspec
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


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
        if matches_file_pattern(normalized_path, pattern):
            # Use custom message or default
            if not message:
                message = f"Sensitive file access prevented for safety: {pattern}"

            return (permission_level, message, pattern)

    return None


def matches_file_pattern(file_path: str, pattern: str) -> bool:
    """
    Check if a file path matches a gitignore-style pattern.

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

    # Treat pattern as global if it doesn't start with / or contain /
    if "/" not in pattern and not pattern.startswith("**"):
        pattern = f"**/{pattern}"

    # Create pathspec matcher
    spec = pathspec.PathSpec.from_lines("gitwildmatch", [pattern])

    # Check match
    matches = spec.match_file(file_path)

    # For negation patterns (!), we want to match only files that match the pattern
    # For regular patterns, we want to match files that match the pattern
    # Both return True when the file matches the pattern (after removing !)
    return matches


def extract_file_from_bash(command: str) -> Optional[str]:
    """
    Extract file path from bash command for pattern matching.

    Args:
        command: Bash command string

    Returns:
        Extracted file path or None
    """
    # Common patterns for file operations in bash
    file_patterns = [
        r"cat\s+(\S+)",
        r"echo\s+.*>\s*(\S+)",
        r"touch\s+(\S+)",
        r"cp\s+\S+\s+(\S+)",
        r"mv\s+\S+\s+(\S+)",
        r"rm\s+.*\s+(\S+)",
    ]

    import re

    for pattern in file_patterns:
        match = re.search(pattern, command)
        if match:
            return match.group(1)

    return None
