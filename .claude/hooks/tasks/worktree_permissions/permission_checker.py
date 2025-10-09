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
            decisions = []
            for cmd in commands:
                # Create tool_input for individual command
                cmd_input = {"command": cmd}
                result = check_single_command_permission(
                    "Bash", cmd_input, context, config, cwd
                )
                decisions.append(result.decision)

            most_restrictive = get_most_restrictive_permission(*decisions)
            return PermissionResult(
                decision=most_restrictive,
                reason=f"Multiple commands in chain, most restrictive: {most_restrictive}"
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
    for pattern in config.global_config.always_deny:
        if match_tool_pattern(tool_name, tool_input, pattern):
            return PermissionResult(
                decision="deny",
                reason=f"Tool blocked by always_deny rule",
                matched_pattern=pattern
            )

    # 4. Check always_allow patterns
    for pattern in config.global_config.always_allow:
        if match_tool_pattern(tool_name, tool_input, pattern):
            return PermissionResult(
                decision="allow",
                reason=f"Tool allowed by always_allow rule",
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
                    reason=validation.reason or "cd command blocked",
                    matched_pattern="cd boundary enforcement"
                )
            else:
                return PermissionResult(
                    decision="allow",
                    reason="cd within worktree boundary",
                    matched_pattern="cd boundary enforcement"
                )

    # 6. Check branch-specific permissions
    permission, permission_reason = find_permission_for_tool(
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
                reason=validation_result.reason or "Path outside worktree boundary"
            )

    return PermissionResult(
        decision=permission,
        reason=permission_reason,
        matched_pattern=f"branch_type={context.branch_type}"
    )


def find_permission_for_tool(
    tool_name: str,
    tool_input: Dict[str, Any],
    context: WorktreeContext,
    config: WorktreePermissionsConfig
) -> tuple[str, str]:
    """
    Find the permission level and reason for a tool based on branch type.

    Args:
        tool_name: Tool name
        tool_input: Tool input
        context: Worktree context
        config: Configuration

    Returns:
        Tuple of (permission decision, reason)
    """
    # Main worktree permissions
    if context.is_main and config.main_worktree.enabled:
        for pattern, perm in config.main_worktree.permissions.items():
            if match_tool_pattern(tool_name, tool_input, pattern):
                return perm, "Main worktree permission rule"
        return config.global_config.default_permission, "Default permission"

    # Branch-specific permissions
    if context.branch_type:
        for entry in config.branch_permissions:
            if context.branch_type in entry.branch_types:
                # Found matching branch type
                for pattern, perm in entry.permissions.items():
                    if match_tool_pattern(tool_name, tool_input, pattern):
                        return perm, entry.reason
                # Tool not in branch permissions, use default
                return config.global_config.default_permission, f"{entry.reason} (using default permission)"

    # Unknown branch type, use unknown_branch config
    for pattern, perm in config.unknown_branch.permissions.items():
        if match_tool_pattern(tool_name, tool_input, pattern):
            return perm, config.unknown_branch.reason

    # Nothing matched, use default
    return config.global_config.default_permission, f"{config.unknown_branch.reason} (using default permission)"
