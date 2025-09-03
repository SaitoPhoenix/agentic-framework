#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = ["pyyaml"]
# ///

import json
import sys
import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from utils.hooks_config import load_hook_config, get_log_directory, should_log_to_file


def is_dangerous_rm_command(command):
    """
    Comprehensive detection of dangerous rm commands.
    Matches various forms of rm -rf and similar destructive patterns.
    """
    # Normalize command by removing extra spaces and converting to lowercase
    normalized = " ".join(command.lower().split())

    # Pattern 1: Standard rm -rf variations
    patterns = [
        r"\brm\s+.*-[a-z]*r[a-z]*f",  # rm -rf, rm -fr, rm -Rf, etc.
        r"\brm\s+.*-[a-z]*f[a-z]*r",  # rm -fr variations
        r"\brm\s+--recursive\s+--force",  # rm --recursive --force
        r"\brm\s+--force\s+--recursive",  # rm --force --recursive
        r"\brm\s+-r\s+.*-f",  # rm -r ... -f
        r"\brm\s+-f\s+.*-r",  # rm -f ... -r
    ]

    # Check for dangerous patterns
    for pattern in patterns:
        if re.search(pattern, normalized):
            return True

    # Pattern 2: Check for rm with recursive flag targeting dangerous paths
    dangerous_paths = [
        r"/",  # Root directory
        r"/\*",  # Root with wildcard
        r"~",  # Home directory
        r"~/",  # Home directory path
        r"\$HOME",  # Home environment variable
        r"\.\.",  # Parent directory references
        r"\*",  # Wildcards in general rm -rf context
        r"\.",  # Current directory
        r"\.\s*$",  # Current directory at end of command
    ]

    if re.search(r"\brm\s+.*-[a-z]*r", normalized):  # If rm has recursive flag
        for path in dangerous_paths:
            if re.search(path, normalized):
                return True

    return False


def is_env_file_access(tool_name, tool_input):
    """
    Check if any tool is trying to access .env files containing sensitive data.
    """
    if tool_name in ["Read", "Edit", "MultiEdit", "Write", "Bash"]:
        # Check file paths for file-based tools
        if tool_name in ["Read", "Edit", "MultiEdit", "Write"]:
            file_path = tool_input.get("file_path", "")
            if ".env" in file_path and not file_path.endswith(".env.sample"):
                return True

        # Check bash commands for .env file access
        elif tool_name == "Bash":
            command = tool_input.get("command", "")
            # Pattern to detect .env file access (but allow .env.sample)
            env_patterns = [
                r"\b\.env\b(?!\.sample)",  # .env but not .env.sample
                r"cat\s+.*\.env\b(?!\.sample)",  # cat .env
                r"echo\s+.*>\s*\.env\b(?!\.sample)",  # echo > .env
                r"touch\s+.*\.env\b(?!\.sample)",  # touch .env
                r"cp\s+.*\.env\b(?!\.sample)",  # cp .env
                r"mv\s+.*\.env\b(?!\.sample)",  # mv .env
            ]

            for pattern in env_patterns:
                if re.search(pattern, command):
                    return True

    return False


def load_worktree_permissions() -> Dict[str, Any]:
    """
    Load worktree permissions configuration from config/worktree-permissions.yaml.

    Returns:
        Dictionary containing worktree permissions configuration,
        or empty dict if file doesn't exist or can't be loaded.
    """
    try:
        config_path = Path(__file__).parent / "config" / "worktree-permissions.yaml"
        if config_path.exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        # If config loading fails, return empty dict
        pass
    return {}


def detect_worktree_from_cwd(cwd: str) -> Optional[str]:
    """
    Detect if the current working directory indicates a worktree environment.

    Args:
        cwd: Current working directory path

    Returns:
        Worktree name (e.g., "worktree_feature-auth") if detected, None otherwise
    """
    if not cwd:
        return None

    # Extract directory name from path
    dir_name = Path(cwd).name

    # Check if it follows worktree naming convention
    if dir_name.startswith("worktree_"):
        return dir_name

    return None


def format_tool_identifier(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Format tool name and input into a standardized identifier for permission matching.

    Args:
        tool_name: Name of the tool being used
        tool_input: Input parameters for the tool

    Returns:
        Formatted tool identifier (e.g., "Bash(git status:*)", "Write", etc.)
    """
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if command:
            # Extract command parts and create more specific patterns
            cmd_parts = command.strip().split()
            if len(cmd_parts) >= 2:
                # For multi-part commands like "git status", "npm install"
                return f"Bash({' '.join(cmd_parts[:2])}:*)"
            elif len(cmd_parts) == 1:
                # For single commands like "python", "ls"
                return f"Bash({cmd_parts[0]}:*)"
        return "Bash"

    # For other tools, just return the tool name
    return tool_name


def check_tool_permission(
    tool_identifier: str, worktree_config: Dict[str, Any], global_config: Dict[str, Any]
) -> Tuple[str, str]:
    """
    Check permission for a tool based on worktree and global configuration.

    Args:
        tool_identifier: Formatted tool identifier
        worktree_config: Worktree-specific configuration
        global_config: Global permissions configuration

    Returns:
        Tuple of (permission_decision, reason)
    """
    # Check global always_deny first
    always_deny = global_config.get("always_deny", [])
    for denied_pattern in always_deny:
        if matches_pattern(tool_identifier, denied_pattern):
            return "deny", f"Tool '{tool_identifier}' is globally denied for security"

    # Check global always_allow
    always_allow = global_config.get("always_allow", [])
    for allowed_pattern in always_allow:
        if matches_pattern(tool_identifier, allowed_pattern):
            return "allow", f"Tool '{tool_identifier}' is globally allowed"

    # Check worktree-specific permissions
    worktree_permissions = worktree_config.get("permissions", {})

    # Direct match first
    if tool_identifier in worktree_permissions:
        permission = worktree_permissions[tool_identifier].lower()
        return permission, f"Worktree permission for '{tool_identifier}': {permission}"

    # Pattern matching for tools like Bash(command:*)
    for pattern, permission in worktree_permissions.items():
        if matches_pattern(tool_identifier, pattern):
            perm = permission.lower()
            return (
                perm,
                f"Worktree pattern permission for '{tool_identifier}' (matched '{pattern}'): {perm}",
            )

    # Default permission
    default_perm = global_config.get("default_permission", "Ask").lower()
    return (
        default_perm,
        f"Using default permission for '{tool_identifier}': {default_perm}",
    )


def evaluate_all_checks(
    tool_name: str,
    tool_input: Dict[str, Any],
    input_data: Dict[str, Any],
    hook_config: Dict[str, Any],
) -> Tuple[str, str]:
    """
    Centralized function to evaluate all security and permission checks.

    Args:
        tool_name: Name of the tool being used
        tool_input: Input parameters for the tool
        input_data: Full input data including cwd, etc.
        hook_config: Hook configuration

    Returns:
        Tuple of (permission_decision, reason)
    """
    # Check 1: .env file access (always blocks access to sensitive environment files)
    if is_env_file_access(tool_name, tool_input):
        return (
            "deny",
            "Access to .env files containing sensitive data is prohibited. Use .env.sample for template files instead.",
        )

    # Check 2: Dangerous rm commands (only if enabled in config)
    if hook_config.get("block_dangerous_commands", True):  # Default True for safety
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            if is_dangerous_rm_command(command):
                return (
                    "deny",
                    "Dangerous rm command detected and prevented for security",
                )

    # Check 3: Worktree permissions
    cwd = input_data.get("cwd", "")
    worktree_name = detect_worktree_from_cwd(cwd)

    if worktree_name:
        # We're in a worktree - check permissions
        permissions_config = load_worktree_permissions()

        # Only apply worktree permissions if they're enabled
        if permissions_config.get("global", {}).get("enabled", True):
            worktree_config, global_config = get_worktree_permissions(
                worktree_name, permissions_config
            )

            # Format the tool identifier
            tool_identifier = format_tool_identifier(tool_name, tool_input)

            # Check permission and return the result
            permission, reason = check_tool_permission(
                tool_identifier, worktree_config, global_config
            )

            # Log permission decision if enabled
            if global_config.get("log_permissions", True) and should_log_to_file(
                "pre_tool_use"
            ):
                log_permission_decision(
                    input_data, worktree_name, tool_identifier, permission, reason
                )

            return permission, reason

    # Default: ask if no specific restrictions apply
    return "ask", "No permissions apply - ask user for permission"


def log_permission_decision(
    input_data: Dict[str, Any],
    worktree_name: str,
    tool_identifier: str,
    permission: str,
    reason: str,
) -> None:
    """
    Log permission decision to file if logging is enabled.

    Args:
        input_data: Original input data
        worktree_name: Name of the current worktree
        tool_identifier: Formatted tool identifier
        permission: Permission decision
        reason: Reason for the decision
    """
    permission_log_data = {
        **input_data,
        "worktree_name": worktree_name,
        "tool_identifier": tool_identifier,
        "permission_decision": permission,
        "permission_reason": reason,
    }

    # Ensure log directory exists
    log_dir = get_log_directory()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "pre_tool_use.json"

    # Read existing log data or initialize empty list
    if log_path.exists():
        with open(log_path, "r") as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []

    # Append new data
    log_data.append(permission_log_data)

    # Write back to file with formatting
    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)


def matches_pattern(tool_identifier: str, pattern: str) -> bool:
    """
    Check if a tool identifier matches a permission pattern.

    Args:
        tool_identifier: The tool identifier to check
        pattern: The permission pattern to match against

    Returns:
        True if the pattern matches, False otherwise
    """
    # Exact match
    if tool_identifier == pattern:
        return True

    # Wildcard pattern matching
    if pattern.endswith(":*"):
        pattern_prefix = pattern[:-2]
        return tool_identifier.startswith(pattern_prefix)

    # For bash commands, also check if the base command matches
    if tool_identifier.startswith("Bash(") and pattern.startswith("Bash("):
        # Extract command parts
        tool_cmd = (
            tool_identifier[5:-3]
            if tool_identifier.endswith(":*)")
            else tool_identifier[5:-1]
        )
        pattern_cmd = pattern[5:-3] if pattern.endswith(":*)") else pattern[5:-1]

        # Check for partial command matching (e.g., "git" should match "git status")
        if pattern.endswith(":*"):
            return tool_cmd.startswith(pattern_cmd)

    return False


def match_worktree_patterns(
    worktree_name: str, patterns: list
) -> Optional[Dict[str, Any]]:
    """
    Match worktree name against pattern-based rules.

    Args:
        worktree_name: Name of the current worktree
        patterns: List of pattern configurations

    Returns:
        Matching pattern configuration or None
    """
    for pattern_config in patterns:
        pattern = pattern_config.get("pattern", "")
        if re.match(pattern, worktree_name):
            return pattern_config
    return None


def get_worktree_permissions(
    worktree_name: str, permissions_config: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Get the appropriate permissions configuration for a worktree.

    Args:
        worktree_name: Name of the worktree
        permissions_config: Full permissions configuration

    Returns:
        Tuple of (worktree_config, global_config)
    """
    global_config = permissions_config.get("global", {})

    # Check for exact worktree match first
    worktrees = permissions_config.get("worktrees", {})
    if worktree_name in worktrees:
        return worktrees[worktree_name], global_config

    # Check pattern-based rules
    patterns = permissions_config.get("patterns", [])
    pattern_match = match_worktree_patterns(worktree_name, patterns)
    if pattern_match:
        return pattern_match, global_config

    # Return empty worktree config with global config as fallback
    return {}, global_config


def create_permission_output(decision: str, reason: str) -> Dict[str, Any]:
    """
    Create the hook output in the format expected by Claude Code.

    Args:
        decision: Permission decision ("allow", "deny", or "ask")
        reason: Reason for the decision

    Returns:
        Hook output dictionary
    """
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason,
        }
    }


def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Load configuration
        hook_config = load_hook_config("pre_tool_use")

        # Centralized evaluation of all checks
        permission, reason = evaluate_all_checks(
            tool_name, tool_input, input_data, hook_config
        )

        # Create standardized output for all decisions
        output = create_permission_output(permission, reason)
        print(json.dumps(output))

        # Regular logging for non-worktree calls or when worktree permissions are disabled
        # (Note: Worktree-specific logging is handled within evaluate_all_checks)
        cwd = input_data.get("cwd", "")
        worktree_name = detect_worktree_from_cwd(cwd)
        if not worktree_name and should_log_to_file("pre_tool_use"):
            log_regular_tool_usage(input_data)

        # Single exit point with proper decision handling
        if permission == "deny":
            sys.exit(2)  # Block tool call
        elif permission == "ask":
            sys.exit(1)  # Ask for confirmation
        else:  # "allow"
            sys.exit(0)  # Allow tool call

    except json.JSONDecodeError:
        # Gracefully handle JSON decode errors
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


def log_regular_tool_usage(input_data: Dict[str, Any]) -> None:
    """
    Log regular tool usage for non-worktree calls when logging is enabled.

    Args:
        input_data: Original input data to log
    """
    # Ensure log directory exists
    log_dir = get_log_directory()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "pre_tool_use.json"

    # Read existing log data or initialize empty list
    if log_path.exists():
        with open(log_path, "r") as f:
            try:
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


if __name__ == "__main__":
    main()
