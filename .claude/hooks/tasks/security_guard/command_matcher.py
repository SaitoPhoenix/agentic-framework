#!/usr/bin/env python3
"""
Command Matcher - Pattern matching for dangerous bash commands
"""

import re
from typing import Dict, Any, List, Optional, Tuple

from .shell_parser import (
    extract_all_commands,
    contains_variable_reference,
    extract_variable_references,
)


def check_command_rules(
    tool_name: str,
    tool_input: Dict[str, Any],
    command_rules: List[Dict[str, Any]],
    permission_level: str,
) -> Optional[Tuple[str, str, str]]:
    """
    Check if a tool call matches any command blocking rules.

    Args:
        tool_name: Name of the tool being used
        tool_input: Input parameters for the tool
        command_rules: List of command rule dictionaries
        permission_level: "allow", "ask", or "deny"

    Returns:
        Tuple of (permission, message, matched_command) if match found, None otherwise
    """
    # Only check Bash tool
    if tool_name != "Bash":
        return None

    command = tool_input.get("command", "")
    if not command:
        return None

    # First, check rules with regex patterns against the FULL command
    # This is important for detecting things like "curl ... | sh"
    result = check_full_command_patterns(command, command_rules, permission_level)
    if result:
        return result

    # Then extract all commands (handles chaining, pipes, subshells)
    # and check each extracted command against rules
    all_commands = extract_all_commands(command)

    # Check each extracted command against rules
    for cmd in all_commands:
        result = check_single_command(cmd, command_rules, permission_level)
        if result:
            return result

    return None


def check_full_command_patterns(
    command: str,
    command_rules: List[Dict[str, Any]],
    permission_level: str,
) -> Optional[Tuple[str, str, str]]:
    """
    Check if the full command matches any regex patterns in rules.

    This must be done BEFORE command decomposition to catch patterns like
    "curl ... | sh" which would be lost when commands are split.

    Args:
        command: Full command string
        command_rules: List of command rule dictionaries
        permission_level: "allow", "ask", or "deny"

    Returns:
        Tuple of (permission, message, matched_command) if match found, None otherwise
    """
    normalized_command = " ".join(command.lower().split())

    for rule in command_rules:
        base_command = rule.get("command", "").lower()
        patterns = rule.get("patterns", [])
        message = rule.get("message", "")

        # Only process rules with patterns
        if not patterns:
            continue

        # Check if base command is in the full command
        if base_command not in normalized_command:
            continue

        # Check if any pattern matches
        if matches_any_pattern(command, patterns):
            if not message:
                message = f"Dangerous command prevented for safety: {base_command}"
            return (permission_level, message, base_command)

    return None


def check_single_command(
    command: str,
    command_rules: List[Dict[str, Any]],
    permission_level: str,
) -> Optional[Tuple[str, str, str]]:
    """
    Check a single command against command rules.

    Args:
        command: Single command string to check
        command_rules: List of command rule dictionaries
        permission_level: "allow", "ask", or "deny"

    Returns:
        Tuple of (permission, message, matched_command) if match found, None otherwise
    """
    # Normalize command
    normalized_command = " ".join(command.lower().split())

    # Check each rule
    for rule in command_rules:
        base_command = rule.get("command", "").lower()
        message = rule.get("message", "")
        block_always = rule.get("block_always", False)

        # Check if base command matches
        if not command_matches_base(normalized_command, base_command):
            continue

        # If block_always is true, block regardless of flags/paths
        if block_always:
            if not message:
                message = f"Dangerous command prevented for safety: {base_command}"
            return (permission_level, message, base_command)

        # Get optional conditions
        dangerous_flags = rule.get("flags", [])
        dangerous_paths = rule.get("paths", [])
        patterns = rule.get("patterns", [])

        # If no conditions specified, match on base command alone
        has_conditions = dangerous_flags or dangerous_paths or patterns

        if not has_conditions:
            # No additional conditions, match on base command alone
            if not message:
                message = f"Command matched: {base_command}"
            return (permission_level, message, base_command)

        # When multiple conditions are specified, ALL must match (AND logic)
        # When only one condition is specified, only that one must match

        flags_match = not dangerous_flags or has_dangerous_flags(normalized_command, dangerous_flags)
        paths_match = not dangerous_paths or has_dangerous_paths(command, dangerous_paths)
        patterns_match = not patterns or matches_any_pattern(command, patterns)

        # All specified conditions must match
        if flags_match and paths_match and patterns_match:
            if not message:
                message = f"Dangerous command prevented for safety: {base_command}"
            return (permission_level, message, base_command)

    return None


def command_matches_base(command: str, base_command: str) -> bool:
    """
    Check if command starts with base command.

    Args:
        command: Full normalized command
        base_command: Base command to match

    Returns:
        True if command starts with base_command
    """
    # Handle multi-word base commands like "git push"
    return command.startswith(base_command)


def has_dangerous_flags(command: str, dangerous_flags: List[List[str]]) -> bool:
    """
    Check if command contains dangerous flag combinations.

    Args:
        command: Normalized command string
        dangerous_flags: List of flag combinations (each is a list)

    Returns:
        True if any dangerous flag combination is present
    """
    # Split command into tokens for word-boundary matching
    tokens = command.split()

    for flag_combo in dangerous_flags:
        # Check if all flags in combination are present as whole tokens
        if all(flag.lower() in tokens for flag in flag_combo):
            return True
    return False


def has_dangerous_paths(command: str, dangerous_paths: List[str]) -> bool:
    """
    Check if command contains dangerous paths as literal arguments or variables.

    Matches exact path arguments only, not substrings.
    For example, "/" matches "rm -rf /" but not "rm -rf a/b"

    Also detects variable references which could expand to dangerous paths.

    Args:
        command: Command string (not normalized, to preserve variables)
        dangerous_paths: List of dangerous literal paths

    Returns:
        True if any dangerous path is present as an argument or if variables are present
    """
    # Split command into tokens to check arguments
    tokens = command.split()

    for path in dangerous_paths:
        path_lower = path.lower()

        # Check if this path appears as a literal argument
        for token in tokens:
            if token.lower() == path_lower:
                return True

    # Check if command contains variable references that could be dangerous
    # Variables in paths are inherently risky since we don't know their expansion
    for token in tokens:
        # Skip the command name and flags
        if token.startswith('-'):
            continue

        # Check if token contains variable reference
        if contains_variable_reference(token):
            # Variable could expand to any of the dangerous paths
            return True

    return False


def matches_any_pattern(command: str, patterns: List[str]) -> bool:
    """
    Check if command matches any regex pattern.

    Args:
        command: Command string (not normalized, to preserve case for regex)
        patterns: List of regex patterns

    Returns:
        True if any pattern matches
    """
    for pattern in patterns:
        if re.search(pattern, command):
            return True
    return False
