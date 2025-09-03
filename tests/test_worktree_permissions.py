#!/usr/bin/env python3
"""
Test script for worktree permissions functionality.
This script simulates different tool calls and worktree environments.
"""

import json
import subprocess
import sys
from pathlib import Path


def test_permission_check(tool_name: str, tool_input: dict, cwd: str = "") -> dict:
    """
    Test the pre_tool_use.py hook with given parameters.

    Args:
        tool_name: Name of the tool to test
        tool_input: Tool input parameters
        cwd: Current working directory (simulates worktree path)

    Returns:
        Hook output or error information
    """

    # Create test input data
    test_input = {
        "session_id": "test-session",
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "cwd": cwd,
    }

    try:
        # Run the hook script
        hook_path = Path("../.claude/hooks/pre_tool_use.py")
        result = subprocess.run(
            [str(hook_path)],
            input=json.dumps(test_input),
            text=True,
            capture_output=True,
            cwd=Path.cwd(),
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "test_input": test_input,
        }

    except Exception as e:
        return {"error": str(e), "test_input": test_input}


def main():
    print("Testing Worktree Permissions Hook")
    print("=" * 40)

    # Test cases
    test_cases = [
        {
            "name": "Regular directory - Write tool",
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/test.txt", "content": "test"},
            "cwd": "/regular/directory",
        },
        {
            "name": "Worktree dev - Write tool (should allow)",
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/test.txt", "content": "test"},
            "cwd": "/path/to/worktree_dev",
        },
        {
            "name": "Worktree main - Write tool (should ask)",
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/test.txt", "content": "test"},
            "cwd": "/path/to/worktree_main",
        },
        {
            "name": "Worktree test - git push (should deny)",
            "tool_name": "Bash",
            "tool_input": {"command": "git push origin main"},
            "cwd": "/path/to/worktree_test",
        },
        {
            "name": "Worktree feature - git status (should allow globally)",
            "tool_name": "Bash",
            "tool_input": {"command": "git status"},
            "cwd": "/path/to/worktree_feature-auth",
        },
        {
            "name": "Any worktree - sudo command (should deny globally)",
            "tool_name": "Bash",
            "tool_input": {"command": "sudo rm -rf /"},
            "cwd": "/path/to/worktree_dev",
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 50)

        result = test_permission_check(
            test_case["tool_name"], test_case["tool_input"], test_case["cwd"]
        )

        print(f"Exit Code: {result.get('exit_code', 'ERROR')}")

        if result.get("stdout"):
            try:
                output_data = json.loads(result["stdout"])
                permission_output = output_data.get("hookSpecificOutput", {})
                print(
                    f"Permission Decision: {permission_output.get('permissionDecision', 'N/A')}"
                )
                print(
                    f"Reason: {permission_output.get('permissionDecisionReason', 'N/A')}"
                )
            except json.JSONDecodeError:
                print(f"Raw Output: {result['stdout']}")

        if result.get("stderr"):
            print(f"Error: {result['stderr']}")

        if result.get("error"):
            print(f"Exception: {result['error']}")


if __name__ == "__main__":
    main()
