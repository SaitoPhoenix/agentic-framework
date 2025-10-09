#!/usr/bin/env python3
"""
Path Validator - Validate that file paths stay within worktree boundaries
"""

from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel


class ValidationResult(BaseModel):
    """Result of path validation"""
    is_valid: bool
    reason: Optional[str] = None
    violating_path: Optional[str] = None


def validate_cd_command(target_dir: str, cwd: str, worktree_root: str) -> ValidationResult:
    """
    Validate that a cd command stays within worktree boundaries.

    Special handling: cd is ALWAYS allowed within worktree, ALWAYS denied outside.

    Args:
        target_dir: Target directory for cd command
        cwd: Current working directory
        worktree_root: Root path of the worktree

    Returns:
        ValidationResult indicating if cd is allowed
    """
    try:
        # Resolve target directory to absolute path
        if Path(target_dir).is_absolute():
            target_absolute = Path(target_dir).resolve()
        else:
            # Relative path, resolve from cwd
            target_absolute = (Path(cwd) / target_dir).resolve()

        # Check if target is within worktree
        worktree_path = Path(worktree_root).resolve()

        try:
            target_absolute.relative_to(worktree_path)
            # Target is within worktree
            return ValidationResult(is_valid=True)
        except ValueError:
            # Target is outside worktree
            return ValidationResult(
                is_valid=False,
                reason=f"Cannot cd outside worktree boundary: {target_absolute}",
                violating_path=str(target_absolute)
            )

    except Exception as e:
        # Error resolving path, deny for safety
        return ValidationResult(
            is_valid=False,
            reason=f"Error resolving cd target: {e}",
            violating_path=target_dir
        )


def validate_file_path(file_path: str, cwd: str, worktree_root: str) -> ValidationResult:
    """
    Validate that a file path is within worktree boundaries.

    Args:
        file_path: File path to validate
        cwd: Current working directory
        worktree_root: Root path of the worktree

    Returns:
        ValidationResult indicating if path is within worktree
    """
    try:
        # Resolve file path to absolute
        if Path(file_path).is_absolute():
            file_absolute = Path(file_path).resolve()
        else:
            # Relative path, resolve from cwd
            file_absolute = (Path(cwd) / file_path).resolve()

        # Check if file is within worktree
        worktree_path = Path(worktree_root).resolve()

        try:
            file_absolute.relative_to(worktree_path)
            # File is within worktree
            return ValidationResult(is_valid=True)
        except ValueError:
            # File is outside worktree
            return ValidationResult(
                is_valid=False,
                reason=f"File path outside worktree boundary: {file_absolute}",
                violating_path=str(file_absolute)
            )

    except Exception as e:
        # Error resolving path, allow for safety (might be a valid path we can't resolve)
        return ValidationResult(is_valid=True)


def validate_tool_paths(
    tool_name: str,
    tool_input: Dict[str, Any],
    cwd: str,
    worktree_root: str
) -> Optional[ValidationResult]:
    """
    Validate that all file paths in a tool call are within worktree boundaries.

    Special cases:
    - Read tool: ALWAYS allowed (can read outside worktree)
    - cd command: Handled separately with strict enforcement
    - Other tools: Check file_path parameter if present

    Args:
        tool_name: Name of the tool being called
        tool_input: Tool input parameters
        cwd: Current working directory
        worktree_root: Root path of the worktree

    Returns:
        ValidationResult if path is invalid, None if valid or no paths to check
    """
    # Read tool is always allowed to access files outside worktree
    if tool_name == "Read":
        return None

    # Check tools with file_path parameter
    if tool_name in ["Write", "Edit", "MultiEdit", "NotebookEdit"]:
        file_path = tool_input.get("file_path")
        if file_path:
            result = validate_file_path(file_path, cwd, worktree_root)
            if not result.is_valid:
                return result

    # For Bash commands, we could extract file paths, but this is complex
    # and prone to false positives. For now, we only strictly enforce cd.
    # Future enhancement: parse Bash commands for file arguments

    return None  # Valid or no paths to check
