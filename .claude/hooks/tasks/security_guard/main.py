#!/usr/bin/env python3
"""
Security Guard Task - Prevent accidental exposure of sensitive files and dangerous commands
"""

import json
import sys
from typing import Dict, Any, Optional

from .rule_loader import load_security_rules, get_rules_by_permission
from .file_matcher import check_file_rules
from .command_matcher import check_command_rules
from .validator import validate_security_rules


def _get_check_info(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """
    Extract relevant information from tool call for logging.

    Args:
        tool_name: Name of the tool being called
        tool_input: Tool input parameters

    Returns:
        Formatted string with tool and target info
    """
    info_parts = [f"tool={tool_name}"]

    # Extract relevant fields based on tool type
    if tool_name == "Bash":
        if "command" in tool_input:
            cmd = tool_input["command"]
            # Truncate long commands
            if len(cmd) > 60:
                cmd = cmd[:60] + "..."
            info_parts.append(f"command='{cmd}'")
    elif tool_name in ["Read", "Write", "Edit"]:
        if "file_path" in tool_input:
            info_parts.append(f"file='{tool_input['file_path']}'")
    elif tool_name == "Glob":
        if "pattern" in tool_input:
            info_parts.append(f"pattern='{tool_input['pattern']}'")

    return ", ".join(info_parts)


def check_security(
    input_data: Dict[str, Any],
    global_config: Dict[str, Any],
    rules_file: str = "config/security-rules.yaml",
    validate_only: bool = False,
    **kwargs,
) -> Optional[Dict[str, Any]]:
    """
    Security guard task - checks tool calls against security rules.

    Args:
        input_data: The input data received by the hook
        global_config: Global configuration settings
        rules_file: Path to security-rules.yaml (relative to project root)
        validate_only: If True, only validate rules (for session_start)
        **kwargs: Additional configuration parameters (unused)

    Returns:
        Optional dict with hook response structure
    """
    try:
        verbose_logging = global_config.get("verbose_logging", False)
        show_errors = global_config.get("show_errors", False)

        # Load security rules
        rules = load_security_rules(rules_file)

        # Validate-only mode (for session_start hook)
        if validate_only:
            is_valid = validate_security_rules(rules)
            if is_valid:
                if verbose_logging:
                    return {"systemMessage": "Security rules validated successfully"}
                return None
            else:
                if show_errors:
                    return {
                        "systemMessage": "Security rules validation failed",
                        "continue": False,
                        "stopReason": "Security rules validation failed"
                    }
                return None

        # Normal security checking mode
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if not tool_name or not tool_input:
            # No tool to check, allow
            if verbose_logging:
                return {"systemMessage": "No tool to check, allowing"}
            return None

        # Extract relevant info for logging
        if verbose_logging:
            check_info = _get_check_info(tool_name, tool_input)

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
                return create_permission_response(*file_result, verbose_logging, check_info if verbose_logging else None)

            # Check command rules
            cmd_result = check_command_rules(
                tool_name, tool_input, whitelist_rules["commands"], permission
            )
            if cmd_result:
                return create_permission_response(*cmd_result, verbose_logging, check_info if verbose_logging else None)

        # 2. If no whitelist match, check blacklist rules
        for permission in permission_order:
            blacklist_rules = get_rules_by_permission(rules, "blacklist", permission)

            # Check file rules
            file_result = check_file_rules(
                tool_name, tool_input, blacklist_rules["files"], permission
            )
            if file_result:
                return create_permission_response(*file_result, verbose_logging, check_info if verbose_logging else None)

            # Check command rules
            cmd_result = check_command_rules(
                tool_name, tool_input, blacklist_rules["commands"], permission
            )
            if cmd_result:
                return create_permission_response(*cmd_result, verbose_logging, check_info if verbose_logging else None)

        # 3. No rules matched - allow (security_guard does nothing)
        if verbose_logging:
            return {"systemMessage": f"No security rules matched for {check_info}, allowing"}
        return None

    except Exception as e:
        # Gracefully handle errors - allow on error to prevent blocking legitimate operations
        if global_config.get("show_errors", False):
            return {"systemMessage": f"Security guard error: {e}"}
        return None


def create_permission_response(
    permission: str, message: str, matched_pattern: str, verbose_logging: bool, check_info: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create permission decision response structure.

    Args:
        permission: "allow", "ask", or "deny"
        message: Reason for the decision
        matched_pattern: The pattern that matched
        verbose_logging: Whether to include system message
        check_info: Optional tool/command info for logging

    Returns:
        Hook response dict with hookSpecificOutput
    """
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": permission,
            "permissionDecisionReason": message,
        }
    }

    # Add system message if verbose logging is enabled
    if verbose_logging:
        if check_info:
            response["systemMessage"] = f"Security check for {check_info}\nDecision: {permission.upper()}\nReason: {message}\nMatched pattern: {matched_pattern}"
        else:
            response["systemMessage"] = f"Security decision: {permission} - {message}"

    return response
