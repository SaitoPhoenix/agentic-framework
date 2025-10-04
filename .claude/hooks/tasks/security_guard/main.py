#!/usr/bin/env python3
"""
Security Guard Task - Prevent accidental exposure of sensitive files and dangerous commands
"""

import json
import sys
from typing import Dict, Any, Optional, Tuple

from .rule_loader import load_security_rules, get_rules_by_permission
from .file_matcher import check_file_rules
from .command_matcher import check_command_rules
from .validator import validate_security_rules


def check_security(
    input_data: Dict[str, Any],
    global_config: Dict[str, Any],
    rules_file: str = "config/security-rules.yaml",
    validate_only: bool = False,
    **kwargs,
) -> None:
    """
    Security guard task - checks tool calls against security rules.

    Args:
        input_data: The input data received by the hook
        global_config: Global configuration settings
        rules_file: Path to security-rules.yaml (relative to project root)
        validate_only: If True, only validate rules and exit (for session_start)
        **kwargs: Additional configuration parameters (unused)
    """
    try:
        # Load security rules
        rules = load_security_rules(rules_file)

        # Validate-only mode (for session_start hook)
        if validate_only:
            is_valid = validate_security_rules(rules)
            if is_valid:
                print("✓ Security rules validated successfully")
                sys.exit(0)
            else:
                print("✗ Security rules validation failed", file=sys.stderr)
                sys.exit(1)

        # Normal security checking mode
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if not tool_name or not tool_input:
            # No tool to check, allow
            sys.exit(0)

        # Check rules in order: whitelist first (highest precedence)
        permission_order = ["deny", "ask", "allow"]

        # 1. Check whitelist rules
        for permission in permission_order:
            whitelist_rules = get_rules_by_permission(rules, "whitelist", permission)

            # Check file rules
            file_result = check_file_rules(
                tool_name, tool_input, whitelist_rules["files"], permission
            )
            if file_result:
                output_permission_decision(*file_result)
                return

            # Check command rules
            cmd_result = check_command_rules(
                tool_name, tool_input, whitelist_rules["commands"], permission
            )
            if cmd_result:
                output_permission_decision(*cmd_result)
                return

        # 2. If no whitelist match, check blacklist rules
        for permission in permission_order:
            blacklist_rules = get_rules_by_permission(rules, "blacklist", permission)

            # Check file rules
            file_result = check_file_rules(
                tool_name, tool_input, blacklist_rules["files"], permission
            )
            if file_result:
                output_permission_decision(*file_result)
                return

            # Check command rules
            cmd_result = check_command_rules(
                tool_name, tool_input, blacklist_rules["commands"], permission
            )
            if cmd_result:
                output_permission_decision(*cmd_result)
                return

        # 3. No rules matched - allow (security_guard does nothing)
        sys.exit(0)

    except Exception as e:
        # Gracefully handle errors
        verbose_errors = global_config.get("verbose_errors", False)
        if verbose_errors:
            print(f"Security guard error: {e}", file=sys.stderr)
        sys.exit(0)  # Allow on error to prevent blocking legitimate operations


def output_permission_decision(
    permission: str, message: str, matched_pattern: str
) -> None:
    """
    Output permission decision and exit with appropriate code.

    Args:
        permission: "allow", "ask", or "deny"
        message: Reason for the decision
        matched_pattern: The pattern that matched
    """
    # Create hook output
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": permission,
            "permissionDecisionReason": message,
        }
    }

    # Print JSON output for Claude Code
    print(json.dumps(output))

    # Log to stderr if verbose
    # (Could extend this to use log_hook in the future)

    # Exit with appropriate code
    if permission == "deny":
        sys.exit(2)  # Block tool call
    elif permission == "ask":
        sys.exit(1)  # Ask for confirmation
    else:  # "allow"
        sys.exit(0)  # Allow tool call
