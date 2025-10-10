#!/usr/bin/env python3
"""
Permission Checker - Check tool permissions based on worktree context
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

from .config_loader import WorktreePermissionsConfig, match_tool_pattern
from .detector import WorktreeContext
from .command_splitter import split_bash_command, extract_cd_target
from .path_validator import validate_cd_command, validate_tool_paths


class PermissionResult(BaseModel):
    """Result of permission check"""
    decision: str  # "allow", "ask", "deny", or "ignore"
    reason: str
    matched_pattern: Optional[str] = None


def format_reason_with_pattern(reason: str, pattern: Optional[str]) -> str:
    """
    Prepend matched pattern to reason if pattern exists.

    Args:
        reason: The permission reason
        pattern: The matched pattern (None if no pattern matched)

    Returns:
        Formatted reason with pattern prefix
    """
    if pattern:
        return f"[{pattern}] {reason}"
    return reason


def get_most_restrictive_permission(*decisions: str) -> str:
    """
    Get the most restrictive permission from a list.

    Precedence: deny > ask > allow > ignore

    Args:
        *decisions: Permission decision strings

    Returns:
        Most restrictive decision
    """
    precedence = {"deny": 4, "ask": 3, "allow": 2, "ignore": 1}

    most_restrictive = "ignore"
    max_precedence = 0

    for decision in decisions:
        if decision in precedence:
            if precedence[decision] > max_precedence:
                max_precedence = precedence[decision]
                most_restrictive = decision

    return most_restrictive


def select_most_restrictive_result(results: list) -> PermissionResult:
    """
    Select the most restrictive PermissionResult from a list.

    Precedence: deny > ask > allow > ignore

    Args:
        results: List of PermissionResult objects

    Returns:
        The most restrictive PermissionResult
    """
    precedence = {"deny": 4, "ask": 3, "allow": 2, "ignore": 1}

    most_restrictive = results[0]
    max_precedence = precedence.get(most_restrictive.decision, 0)

    for result in results[1:]:
        if precedence.get(result.decision, 0) > max_precedence:
            max_precedence = precedence[result.decision]
            most_restrictive = result

    return most_restrictive


def check_tool_permission(
    tool_name: str,
    tool_input: Dict[str, Any],
    context: WorktreeContext,
    config: WorktreePermissionsConfig,
    cwd: str
) -> PermissionResult:
    """
    Check permission for a tool based on worktree context and configuration.

    Logic flow:
    1. If main worktree and main_worktree.enabled=false → ignore
    2. If Bash tool, split by separators and check each command
    3. Check always_deny list → deny
    4. Check always_allow list → allow
    5. Special: cd command → validate boundary
    6. Lookup branch type permissions
    7. Fall back to unknown_branch or default_permission

    Args:
        tool_name: Name of the tool being called
        tool_input: Tool input parameters
        context: Worktree context information
        config: Loaded configuration
        cwd: Current working directory

    Returns:
        PermissionResult with decision and reason
    """
    # 1. Main worktree handling
    if context.is_main and not config.main_worktree.enabled:
        return PermissionResult(
            decision="ignore",
            reason="Main worktree permissions are disabled"
        )

    # 2. Bash command handling - split and check each command
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        commands = split_bash_command(command)

        if len(commands) > 1:
            # Multiple commands, check each and return most restrictive
            results = []
            for cmd in commands:
                # Create tool_input for individual command
                cmd_input = {"command": cmd}
                result = check_single_command_permission(
                    "Bash", cmd_input, context, config, cwd
                )
                results.append(result)

            # Find the most restrictive result
            most_restrictive_result = select_most_restrictive_result(results)

            return PermissionResult(
                decision=most_restrictive_result.decision,
                reason=most_restrictive_result.reason,
                matched_pattern=most_restrictive_result.matched_pattern
            )

    # Single command or non-Bash tool
    return check_single_command_permission(tool_name, tool_input, context, config, cwd)


def check_single_command_permission(
    tool_name: str,
    tool_input: Dict[str, Any],
    context: WorktreeContext,
    config: WorktreePermissionsConfig,
    cwd: str
) -> PermissionResult:
    """
    Check permission for a single tool/command.

    Args:
        tool_name: Name of the tool
        tool_input: Tool input parameters
        context: Worktree context
        config: Configuration
        cwd: Current working directory

    Returns:
        PermissionResult
    """
    # 3. Check always_deny patterns
    for rule in config.global_config.always_deny:
        if match_tool_pattern(tool_name, tool_input, rule.pattern):
            return PermissionResult(
                decision="deny",
                reason=format_reason_with_pattern(rule.reason, rule.pattern),
                matched_pattern=rule.pattern
            )

    # 4. Check always_allow patterns
    for pattern in config.global_config.always_allow:
        if match_tool_pattern(tool_name, tool_input, pattern):
            return PermissionResult(
                decision="allow",
                reason=format_reason_with_pattern("Tool allowed by always_allow rule", pattern),
                matched_pattern=pattern
            )

    # 5. Special case: cd command boundary check
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        cd_target = extract_cd_target(command)

        if cd_target:
            # This is a cd command, validate boundary
            validation = validate_cd_command(cd_target, cwd, context.worktree_root)

            if not validation.is_valid:
                return PermissionResult(
                    decision="deny",
                    reason=format_reason_with_pattern(
                        validation.reason or "cd command blocked",
                        "Bash(cd:*)"
                    ),
                    matched_pattern="Bash(cd:*)"
                )
            else:
                return PermissionResult(
                    decision="allow",
                    reason=format_reason_with_pattern(
                        "cd within worktree boundary",
                        "Bash(cd:*)"
                    ),
                    matched_pattern="Bash(cd:*)"
                )

    # 6. Check branch-specific permissions
    permission, permission_reason, matched_pattern = find_permission_for_tool(
        tool_name, tool_input, context, config
    )

    # 7. Path boundary validation (if enforce_boundaries=true and not in main worktree)
    if config.global_config.enforce_boundaries and not context.is_main:
        validation_result = validate_tool_paths(
            tool_name, tool_input, cwd, context.worktree_root
        )

        if validation_result and not validation_result.is_valid:
            return PermissionResult(
                decision="deny",
                reason=format_reason_with_pattern(
                    validation_result.reason or "Path outside worktree boundary",
                    tool_name
                ),
                matched_pattern=tool_name
            )

    return PermissionResult(
        decision=permission,
        reason=format_reason_with_pattern(permission_reason, matched_pattern),
        matched_pattern=matched_pattern
    )


def find_permission_for_tool(
    tool_name: str,
    tool_input: Dict[str, Any],
    context: WorktreeContext,
    config: WorktreePermissionsConfig
) -> tuple[str, str, Optional[str]]:
    """
    Find the permission level, reason, and matched pattern for a tool based on branch type.

    When multiple patterns match, returns the most restrictive permission.

    Args:
        tool_name: Tool name
        tool_input: Tool input
        context: Worktree context
        config: Configuration

    Returns:
        Tuple of (permission decision, reason, matched_pattern)
    """
    matches = []  # List of (permission, reason, pattern) tuples

    # Main worktree permissions
    if context.is_main and config.main_worktree.enabled:
        for pattern, perm in config.main_worktree.permissions.items():
            if match_tool_pattern(tool_name, tool_input, pattern):
                matches.append((perm, "Main worktree permission rule", pattern))

        if matches:
            return select_most_restrictive_match(matches)
        return config.global_config.default_permission, "Default permission", None

    # Branch-specific permissions
    if context.branch_type:
        for entry in config.branch_permissions:
            if context.branch_type in entry.branch_types:
                # Found matching branch type
                for pattern, perm in entry.permissions.items():
                    if match_tool_pattern(tool_name, tool_input, pattern):
                        matches.append((perm, entry.reason, pattern))

                if matches:
                    return select_most_restrictive_match(matches)
                # Tool not in branch permissions, use default
                return config.global_config.default_permission, f"{entry.reason} (using default permission)", None

    # Unknown branch type, use unknown_branch config
    for pattern, perm in config.unknown_branch.permissions.items():
        if match_tool_pattern(tool_name, tool_input, pattern):
            matches.append((perm, config.unknown_branch.reason, pattern))

    if matches:
        return select_most_restrictive_match(matches)

    # Nothing matched, use default
    return config.global_config.default_permission, f"{config.unknown_branch.reason} (using default permission)", None


def select_most_restrictive_match(matches: list) -> tuple[str, str, str]:
    """
    Select the most restrictive permission from a list of matches.

    Args:
        matches: List of (permission, reason, pattern) tuples

    Returns:
        The most restrictive match tuple
    """
    precedence = {"deny": 4, "ask": 3, "allow": 2, "ignore": 1}

    most_restrictive = matches[0]
    max_precedence = precedence.get(most_restrictive[0], 0)

    for match in matches[1:]:
        perm = match[0]
        if precedence.get(perm, 0) > max_precedence:
            max_precedence = precedence[perm]
            most_restrictive = match

    return most_restrictive
