#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = ["pyyaml"]
# ///

"""
Test script for settings.json permissions functionality.
This script tests the new permission checking logic in pre_tool_use.py.
"""

import sys
import json
from pathlib import Path

# Add the hooks directory to sys.path to import the module
hooks_dir = Path(__file__).parent.parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(hooks_dir))

from pre_tool_use import (
    load_settings_permissions,
    check_tool_permission,
    format_tool_identifier,
    matches_pattern,
)


def test_load_settings_permissions():
    """Test loading permissions from settings.json"""
    print("Testing load_settings_permissions()...")
    permissions = load_settings_permissions()
    print(f"Loaded permissions: {permissions}")

    # Check if we have the expected structure
    assert isinstance(permissions, dict), "Permissions should be a dictionary"
    assert "allow" in permissions, "Should have 'allow' key"
    assert "deny" in permissions, "Should have 'deny' key"
    assert isinstance(permissions["allow"], list), "Allow should be a list"
    assert isinstance(permissions["deny"], list), "Deny should be a list"

    print("✓ Settings permissions loaded successfully")
    return permissions


def test_tool_identifier_formatting():
    """Test tool identifier formatting"""
    print("\nTesting format_tool_identifier()...")

    # Test Bash command formatting
    test_cases = [
        (("Bash", {"command": "uv sync"}), "Bash(uv sync:*)"),
        (("Bash", {"command": "git status"}), "Bash(git status:*)"),
        (("Bash", {"command": "mkdir test"}), "Bash(mkdir test:*)"),
        (("Bash", {"command": "ls"}), "Bash(ls:*)"),
        (("Write", {"file_path": "/tmp/test.txt"}), "Write"),
        (("Edit", {"file_path": "/tmp/test.txt"}), "Edit"),
    ]

    for (tool_name, tool_input), expected in test_cases:
        result = format_tool_identifier(tool_name, tool_input)
        assert result == expected, f"Expected {expected}, got {result}"
        print(f"✓ {tool_name} -> {result}")


def test_pattern_matching():
    """Test pattern matching functionality"""
    print("\nTesting pattern matching...")

    test_cases = [
        ("Bash(uv sync:*)", "Bash(uv:*)", True),
        ("Bash(mkdir test:*)", "Bash(mkdir:*)", True),
        ("Write", "Write", True),
        ("Bash(rm -rf:*)", "Bash(uv:*)", False),
        ("Edit", "Write", False),
    ]

    for tool_identifier, pattern, expected in test_cases:
        result = matches_pattern(tool_identifier, pattern)
        assert result == expected, (
            f"Pattern matching failed for {tool_identifier} vs {pattern}"
        )
        status = "✓" if result == expected else "✗"
        print(f"{status} {tool_identifier} matches {pattern}: {result}")


def test_permission_checking():
    """Test the complete permission checking logic"""
    print("\nTesting permission checking logic...")

    # Test cases with expected outcomes
    test_cases = [
        # Tool that should be allowed by settings.json
        ("Bash", {"command": "uv sync"}, "allow", "settings.json"),
        ("Write", {}, "allow", "settings.json"),
        # Tool that would fall back to default (not in settings.json)
        ("Read", {"file_path": "/tmp/test.txt"}, "ask", "default"),
        # Bash command not in allow list
        ("Bash", {"command": "rm -rf /"}, "ask", "default"),
    ]

    for tool_name, tool_input, expected_decision, expected_source in test_cases:
        tool_identifier = format_tool_identifier(tool_name, tool_input)

        # Mock empty worktree and global configs to test settings.json priority
        worktree_config = {}
        global_config = {
            "default_permission": "ask",
            "always_allow": [],
            "always_deny": [],
        }

        decision, reason = check_tool_permission(
            tool_identifier, worktree_config, global_config
        )

        print(f"Tool: {tool_identifier}")
        print(f"Decision: {decision}")
        print(f"Reason: {reason}")

        assert decision == expected_decision, (
            f"Expected {expected_decision}, got {decision}"
        )

        if expected_source == "settings.json":
            assert "settings.json" in reason, (
                f"Expected settings.json in reason, got: {reason}"
            )
        elif expected_source == "default":
            assert "default" in reason.lower(), (
                f"Expected default in reason, got: {reason}"
            )

        print(f"✓ {tool_name} permission check passed")
        print()


def main():
    """Run all tests"""
    print("Starting settings.json permissions tests...\n")

    try:
        # Test 1: Load settings permissions
        permissions = test_load_settings_permissions()

        # Test 2: Tool identifier formatting
        test_tool_identifier_formatting()

        # Test 3: Pattern matching
        test_pattern_matching()

        # Test 4: Complete permission checking
        test_permission_checking()

        print("🎉 All tests passed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
