#!/usr/bin/env python3
"""
Worktree Permissions Task - Manage tool permissions based on git worktree context

This task enforces tool usage restrictions based on:
1. Whether code is running in a git worktree (main or linked)
2. The type of branch (feat, fix, test, etc.)
3. Path boundaries (prevent operations outside worktree)

Permission decisions:
- ignore: Pass through, no permission decision sent
- allow: Explicitly allow the tool
- ask: Require user confirmation
- deny: Block the tool completely
"""

import json
import sys
from typing import Dict, Any, Optional

from .config_loader import load_config
from .detector import detect_worktree_context
from .permission_checker import check_tool_permission


def check_permissions(
    input_data: Dict[str, Any],
    global_config: Dict[str, Any],
    config_file: str = ".claude/hooks/config/worktree-permissions.yaml",
    **kwargs,
) -> Optional[Dict[str, Any]]:
    """
    Worktree permissions task - check tool calls against worktree-based permissions.

    Args:
        input_data: The input data received by the hook
        global_config: Global configuration settings
        config_file: Path to worktree-permissions.yaml (relative to project root)
        **kwargs: Additional configuration parameters (unused)

    Returns:
        Optional dict with hook response structure
    """
    try:
        verbose_logging = global_config.get("verbose_logging", False)
        show_errors = global_config.get("show_errors", False)

        # Load configuration
        config = load_config(config_file)

        # Check if worktree permissions are enabled
        if not config.global_config.enabled:
            if verbose_logging:
                return {"systemMessage": "Worktree permissions are disabled"}
            return None

        # Extract input data
        cwd = input_data.get("cwd", "")
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        if not tool_name or not tool_input:
            # No tool to check, pass through
            if verbose_logging:
                return {"systemMessage": "No tool to check, passing through"}
            return None

        # Validate cwd exists
        from pathlib import Path
        cwd_path = Path(cwd)
        if not cwd_path.exists():
            if show_errors:
                return {"systemMessage": f"Worktree permissions: Current working directory does not exist: {cwd}"}
            return None
        if not cwd_path.is_dir():
            if show_errors:
                return {"systemMessage": f"Worktree permissions: Current working directory is not a directory: {cwd}"}
            return None

        # Detect worktree context
        context = detect_worktree_context(cwd)

        if context is None:
            # Not in a git worktree, pass through
            if verbose_logging:
                return {"systemMessage": "Not in a git worktree, passing through"}
            return None

        # Check tool permission
        result = check_tool_permission(
            tool_name=tool_name,
            tool_input=tool_input,
            context=context,
            config=config,
            cwd=cwd
        )

        # Create response based on decision
        return create_permission_response(
            decision=result.decision,
            reason=result.reason,
            matched_pattern=result.matched_pattern,
            verbose_logging=verbose_logging,
            tool_name=tool_name,
            context=context
        )

    except Exception as e:
        # Gracefully handle errors - pass through on error
        if global_config.get("show_errors", False):
            return {"systemMessage": f"Worktree permissions error: {e}"}
        return None


def create_permission_response(
    decision: str,
    reason: str,
    matched_pattern: Optional[str],
    verbose_logging: bool,
    tool_name: str,
    context: Any
) -> Optional[Dict[str, Any]]:
    """
    Create hook response based on permission decision.

    Response mapping:
    - ignore → None (no output)
    - allow → hookSpecificOutput with permissionDecision="allow"
    - ask → hookSpecificOutput with permissionDecision="ask"
    - deny → hookSpecificOutput with permissionDecision="deny"

    Args:
        decision: Permission decision (ignore, allow, ask, deny)
        reason: Reason for the decision
        matched_pattern: Pattern that matched (if any)
        verbose_logging: Whether to include verbose system message
        tool_name: Name of the tool being checked
        context: Worktree context

    Returns:
        Hook response dictionary or None
    """
    # ignore → return None (pass through)
    if decision == "ignore":
        if verbose_logging:
            return {"systemMessage": f"Worktree permissions: IGNORE - {reason}"}
        return None

    # Build response for allow, ask, deny
    response = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
            "permissionDecisionReason": reason
        }
    }

    # Add verbose system message if enabled
    if verbose_logging:
        context_info = f"worktree={context.worktree_root}, branch={context.branch_name}, type={context.branch_type}"
        response["systemMessage"] = (
            f"Worktree permission check for tool={tool_name}\n"
            f"Context: {context_info}\n"
            f"Decision: {decision.upper()}\n"
            f"Reason: {reason}\n"
            f"Pattern: {matched_pattern or 'N/A'}"
        )

    return response
