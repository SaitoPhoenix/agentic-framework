#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = ["pyyaml"]
# ///

"""
Focused test for settings.json permissions functionality.
This test validates that the new settings.json permission checking works correctly.
"""

import json
import subprocess
import tempfile
import sys
from pathlib import Path


def test_settings_json_allow():
    """Test that tools in settings.json allow list are permitted"""
    print("Testing settings.json allow functionality...")

    # Create a temporary directory that's NOT a worktree
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use Write tool which is in settings.json allow list
        input_data = {
            "tool_name": "Write",
            "tool_input": {"file_path": f"{temp_dir}/test.txt", "content": "test"},
            "cwd": temp_dir,  # Non-worktree directory
        }

        # Run the hook
        result = subprocess.run(
            ["uv", "run", "../../.claude/hooks/pre_tool_use.py"],
            input=json.dumps(input_data),
            text=True,
            capture_output=True,
            cwd=Path.cwd(),  # Run from our current directory where the hook exists
        )

        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        # Should exit with code 0 (allow)
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

        # Parse output
        output = json.loads(result.stdout)
        hook_output = output["hookSpecificOutput"]

        assert hook_output["permissionDecision"] == "allow"
        print(f"Reason: {hook_output['permissionDecisionReason']}")

        # Should be allowed either by settings.json or by default "allow" for non-worktree
        print("✓ Settings.json allow test passed")


def test_settings_json_deny():
    """Test that tools in settings.json deny list are blocked"""
    print("\nTesting settings.json deny functionality...")

    # First, add a deny entry to settings.json
    settings_path = Path("../../.claude/settings.json")
    with open(settings_path, "r") as f:
        settings = json.load(f)

    # Temporarily add a deny entry for a tool that's NOT in the allow list
    original_deny = settings["permissions"]["deny"].copy()
    settings["permissions"]["deny"].append("Read")

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

    try:
        # Create a temporary directory that's NOT a worktree
        with tempfile.TemporaryDirectory() as temp_dir:
            # Use Read tool which we just added to deny list
            input_data = {
                "tool_name": "Read",
                "tool_input": {"file_path": f"{temp_dir}/test.txt"},
                "cwd": temp_dir,  # Non-worktree directory
            }

            # Run the hook
            result = subprocess.run(
                ["uv", "run", "../../.claude/hooks/pre_tool_use.py"],
                input=json.dumps(input_data),
                text=True,
                capture_output=True,
                cwd=Path.cwd(),  # Run from our current directory where the hook exists
            )

            print(f"Exit code: {result.returncode}")
            print(f"Stdout: {result.stdout}")
            if result.stderr:
                print(f"Stderr: {result.stderr}")

            # Should exit with code 2 (deny)
            assert result.returncode == 2, (
                f"Expected exit code 2, got {result.returncode}"
            )

            # Parse output
            output = json.loads(result.stdout)
            hook_output = output["hookSpecificOutput"]

            assert hook_output["permissionDecision"] == "deny"
            assert "settings.json" in hook_output["permissionDecisionReason"]

            print("✓ Settings.json deny test passed")

    finally:
        # Restore original settings
        settings["permissions"]["deny"] = original_deny
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)


def test_settings_json_fallback():
    """Test that unknown tools fall back to default when not in settings.json"""
    print("\nTesting settings.json fallback to default...")

    # Create a temporary directory that's NOT a worktree
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use a tool that's NOT in settings.json allow or deny
        input_data = {
            "tool_name": "Read",
            "tool_input": {"file_path": f"{temp_dir}/test.txt"},
            "cwd": temp_dir,  # Non-worktree directory
        }

        # Run the hook
        result = subprocess.run(
            ["uv", "run", "../../.claude/hooks/pre_tool_use.py"],
            input=json.dumps(input_data),
            text=True,
            capture_output=True,
            cwd=Path.cwd(),  # Run from our current directory where the hook exists
        )

        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        # Should exit with code 0 (allow) since there are no restrictions outside worktree
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

        # Parse output
        output = json.loads(result.stdout)
        hook_output = output["hookSpecificOutput"]

        assert hook_output["permissionDecision"] == "allow"
        print(f"Reason: {hook_output['permissionDecisionReason']}")

        print("✓ Settings.json fallback test passed")


def test_bash_command_in_settings():
    """Test that Bash commands in settings.json work correctly"""
    print("\nTesting Bash command in settings.json...")

    # Create a temporary directory that's NOT a worktree
    with tempfile.TemporaryDirectory() as temp_dir:
        # Use a bash command that's in settings.json allow list
        input_data = {
            "tool_name": "Bash",
            "tool_input": {"command": "mkdir test_dir"},
            "cwd": temp_dir,  # Non-worktree directory
        }

        # Run the hook
        result = subprocess.run(
            ["uv", "run", "../../.claude/hooks/pre_tool_use.py"],
            input=json.dumps(input_data),
            text=True,
            capture_output=True,
            cwd=Path.cwd(),  # Run from our current directory where the hook exists
        )

        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        # Should exit with code 0 (allow)
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}"

        # Parse output
        output = json.loads(result.stdout)
        hook_output = output["hookSpecificOutput"]

        assert hook_output["permissionDecision"] == "allow"
        print(f"Reason: {hook_output['permissionDecisionReason']}")

        print("✓ Bash command in settings.json test passed")


def main():
    """Run all focused tests for settings.json functionality"""
    print("Starting focused tests for settings.json permissions...\n")

    try:
        test_settings_json_allow()
        test_settings_json_deny()
        test_settings_json_fallback()
        test_bash_command_in_settings()

        print("\n🎉 All focused tests passed successfully!")
        print("Settings.json permissions feature is working correctly!")

    except Exception as e:
        print(f"\n❌ Focused test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
