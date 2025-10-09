#!/usr/bin/env python3
"""
Worktree Detector - Detect git worktree context and extract branch information
"""

import subprocess
import re
from pathlib import Path
from typing import Optional
from pydantic import BaseModel


class WorktreeContext(BaseModel):
    """Context information about the current worktree"""
    is_worktree: bool  # True if in any git worktree (main or linked)
    is_main: bool  # True if in main worktree
    worktree_root: str  # Absolute path to worktree root
    branch_name: Optional[str] = None  # Full branch name (e.g., "feat/new-feature")
    branch_type: Optional[str] = None  # Extracted type (e.g., "feat")


def detect_worktree_context(cwd: str) -> Optional[WorktreeContext]:
    """
    Detect if current working directory is in a git worktree and extract context.

    Detection logic:
    1. Run `git worktree list --porcelain` to get all worktrees
    2. Check if cwd starts with any worktree path
    3. Extract branch name and type from matched worktree
    4. Determine if it's main or linked worktree

    Args:
        cwd: Current working directory from hook input

    Returns:
        WorktreeContext if in a git worktree, None otherwise
    """
    try:
        # Run git worktree list --porcelain
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            # Not in a git repository or git command failed
            return None

        # Parse porcelain output
        worktrees = parse_worktree_list(result.stdout)

        # Find which worktree contains cwd
        cwd_path = Path(cwd).resolve()

        for worktree in worktrees:
            worktree_path = Path(worktree["path"]).resolve()

            # Check if cwd starts with worktree path
            try:
                cwd_path.relative_to(worktree_path)
                # cwd is within this worktree
                is_main = worktree.get("main", False)
                branch_name = worktree.get("branch")
                branch_type = extract_branch_type(branch_name) if branch_name else None

                return WorktreeContext(
                    is_worktree=True,
                    is_main=is_main,
                    worktree_root=str(worktree_path),
                    branch_name=branch_name,
                    branch_type=branch_type
                )
            except ValueError:
                # cwd is not under this worktree, continue
                continue

        # cwd not in any worktree (shouldn't happen if git command succeeded)
        return None

    except subprocess.TimeoutExpired:
        # Git command timed out
        return None
    except Exception:
        # Any other error, pass through gracefully
        return None


def parse_worktree_list(output: str) -> list[dict]:
    """
    Parse `git worktree list --porcelain` output.

    Example output:
        worktree /path/to/main
        HEAD abc123...
        branch refs/heads/main

        worktree /path/to/worktrees/feat-new-ui
        HEAD def456...
        branch refs/heads/feat/new-ui

    Args:
        output: Output from git worktree list --porcelain

    Returns:
        List of worktree dictionaries with keys: path, branch, main
    """
    worktrees = []
    current_worktree = {}

    for line in output.strip().split('\n'):
        line = line.strip()

        if not line:
            # Empty line separates worktrees
            if current_worktree:
                worktrees.append(current_worktree)
                current_worktree = {}
            continue

        if line.startswith('worktree '):
            current_worktree['path'] = line.split(' ', 1)[1]

        elif line.startswith('branch '):
            # Extract branch name from refs/heads/branch-name
            ref = line.split(' ', 1)[1]
            if ref.startswith('refs/heads/'):
                current_worktree['branch'] = ref[len('refs/heads/'):]

        elif line.startswith('bare'):
            current_worktree['bare'] = True

    # Add last worktree
    if current_worktree:
        worktrees.append(current_worktree)

    # Mark the first worktree as main (it's always the main working tree)
    if worktrees:
        worktrees[0]['main'] = True
        for wt in worktrees[1:]:
            wt['main'] = False

    return worktrees


def extract_branch_type(branch_name: str) -> Optional[str]:
    """
    Extract branch type from branch name.

    Expected pattern: TYPE/name
    Examples:
        "feat/new-feature" -> "feat"
        "fix/bug-123" -> "fix"
        "main" -> None (no type)

    Args:
        branch_name: Full branch name

    Returns:
        Branch type string or None if no type found
    """
    if '/' in branch_name:
        return branch_name.split('/', 1)[0]
    return None


def is_path_within_worktree(path: str, worktree_root: str) -> bool:
    """
    Check if a path is within the worktree boundary.

    Args:
        path: File or directory path to check
        worktree_root: Root path of the worktree

    Returns:
        True if path is within worktree
    """
    try:
        path_obj = Path(path).resolve()
        root_obj = Path(worktree_root).resolve()

        # Check if path is relative to worktree root
        path_obj.relative_to(root_obj)
        return True
    except ValueError:
        # path is not relative to worktree_root
        return False
