#!/usr/bin/env python3
"""
Validator - Validate security-rules.yaml structure and content
"""

import sys
from typing import Dict, Any, List


def validate_security_rules(rules: Dict[str, Any]) -> bool:
    """
    Validate security rules structure and content.

    Args:
        rules: Security rules dictionary from YAML

    Returns:
        True if valid, False otherwise (prints errors to stderr)
    """
    if not rules:
        print("Warning: Security rules file is empty", file=sys.stderr)
        return True  # Empty is valid, just no rules

    valid = True
    valid_permissions = ["allow", "ask", "deny"]
    valid_list_types = ["whitelist", "blacklist"]
    valid_tools = ["Read", "Write", "Edit", "MultiEdit", "Bash"]

    # Check top-level structure
    for list_type in rules:
        if list_type not in valid_list_types:
            print(
                f"Error: Invalid list type '{list_type}'. Must be 'whitelist' or 'blacklist'",
                file=sys.stderr,
            )
            valid = False
            continue

        list_rules = rules[list_type]
        if not isinstance(list_rules, dict):
            print(
                f"Error: '{list_type}' must be a dictionary of permissions",
                file=sys.stderr,
            )
            valid = False
            continue

        # Check permission levels
        for permission in list_rules:
            if permission not in valid_permissions:
                print(
                    f"Error: Invalid permission '{permission}' in {list_type}. Must be one of: {valid_permissions}",
                    file=sys.stderr,
                )
                valid = False
                continue

            permission_rules = list_rules[permission]
            if not isinstance(permission_rules, dict):
                print(
                    f"Error: '{list_type}.{permission}' must be a dictionary",
                    file=sys.stderr,
                )
                valid = False
                continue

            # Validate file rules
            if "files" in permission_rules:
                files = permission_rules["files"]
                if not isinstance(files, list):
                    print(
                        f"Error: '{list_type}.{permission}.files' must be a list",
                        file=sys.stderr,
                    )
                    valid = False
                else:
                    for i, file_rule in enumerate(files):
                        if not validate_file_rule(
                            file_rule, f"{list_type}.{permission}.files[{i}]", valid_tools
                        ):
                            valid = False

            # Validate command rules
            if "commands" in permission_rules:
                commands = permission_rules["commands"]
                if not isinstance(commands, list):
                    print(
                        f"Error: '{list_type}.{permission}.commands' must be a list",
                        file=sys.stderr,
                    )
                    valid = False
                else:
                    for i, cmd_rule in enumerate(commands):
                        if not validate_command_rule(
                            cmd_rule,
                            f"{list_type}.{permission}.commands[{i}]",
                            valid_tools,
                        ):
                            valid = False

    return valid


def validate_file_rule(
    rule: Any, path: str, valid_tools: List[str]
) -> bool:
    """
    Validate a single file rule.

    Args:
        rule: File rule to validate
        path: Path in config for error messages
        valid_tools: List of valid tool names

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(rule, dict):
        print(f"Error: {path} must be a dictionary", file=sys.stderr)
        return False

    # Check required 'pattern' field
    if "pattern" not in rule:
        print(f"Error: {path} missing required 'pattern' field", file=sys.stderr)
        return False

    if not isinstance(rule["pattern"], str):
        print(f"Error: {path}.pattern must be a string", file=sys.stderr)
        return False

    # Check optional 'tools' field
    if "tools" in rule:
        tools = rule["tools"]
        if not isinstance(tools, list):
            print(f"Error: {path}.tools must be a list", file=sys.stderr)
            return False

        for tool in tools:
            if tool not in valid_tools:
                print(
                    f"Error: {path}.tools contains invalid tool '{tool}'. Must be one of: {valid_tools}",
                    file=sys.stderr,
                )
                return False

    # Check optional 'message' field
    if "message" in rule and not isinstance(rule["message"], str):
        print(f"Error: {path}.message must be a string", file=sys.stderr)
        return False

    return True


def validate_command_rule(
    rule: Any, path: str, valid_tools: List[str]
) -> bool:
    """
    Validate a single command rule.

    Args:
        rule: Command rule to validate
        path: Path in config for error messages
        valid_tools: List of valid tool names

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(rule, dict):
        print(f"Error: {path} must be a dictionary", file=sys.stderr)
        return False

    # Check required 'command' field
    if "command" not in rule:
        print(f"Error: {path} missing required 'command' field", file=sys.stderr)
        return False

    if not isinstance(rule["command"], str):
        print(f"Error: {path}.command must be a string", file=sys.stderr)
        return False

    # Check optional 'block_always' field
    if "block_always" in rule and not isinstance(rule["block_always"], bool):
        print(f"Error: {path}.block_always must be a boolean", file=sys.stderr)
        return False

    # Check optional 'flags' field
    if "flags" in rule:
        flags = rule["flags"]
        if not isinstance(flags, list):
            print(f"Error: {path}.flags must be a list", file=sys.stderr)
            return False

        for flag_combo in flags:
            if not isinstance(flag_combo, list):
                print(
                    f"Error: {path}.flags must contain lists of flag combinations",
                    file=sys.stderr,
                )
                return False

    # Check optional 'paths' field
    if "paths" in rule:
        paths = rule["paths"]
        if not isinstance(paths, list):
            print(f"Error: {path}.paths must be a list", file=sys.stderr)
            return False

        for path_item in paths:
            if not isinstance(path_item, str):
                print(f"Error: {path}.paths must contain strings", file=sys.stderr)
                return False

    # Check optional 'patterns' field (regex)
    if "patterns" in rule:
        patterns = rule["patterns"]
        if not isinstance(patterns, list):
            print(f"Error: {path}.patterns must be a list", file=sys.stderr)
            return False

        for pattern in patterns:
            if not isinstance(pattern, str):
                print(f"Error: {path}.patterns must contain strings", file=sys.stderr)
                return False

    # Check optional 'tools' field
    if "tools" in rule:
        tools = rule["tools"]
        if not isinstance(tools, list):
            print(f"Error: {path}.tools must be a list", file=sys.stderr)
            return False

        for tool in tools:
            if tool not in valid_tools:
                print(
                    f"Error: {path}.tools contains invalid tool '{tool}'. Must be one of: {valid_tools}",
                    file=sys.stderr,
                )
                return False

    # Check optional 'message' field
    if "message" in rule and not isinstance(rule["message"], str):
        print(f"Error: {path}.message must be a string", file=sys.stderr)
        return False

    return True
