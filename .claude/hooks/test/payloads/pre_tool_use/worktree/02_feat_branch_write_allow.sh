#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
# --- Configuration ---
# You can change the path to your Python hook entrypoint here.
HOOK_SCRIPT_PATH="/mnt/e/DataAlchemy/Repositories/agentic-framework/.claude/hooks/hook_entry.py"
HOOK_NAME="pre_tool_use"

# --- Payload Definition ---
# Define a multi-line JSON payload using a "here document".
# The content is assigned to the PAYLOAD variable.
PAYLOAD=$(cat <<EOF
{
    "session_id": "test-session-002",
    "transcript_path": "test.jsonl",
    "cwd": "/repo/worktrees/feat/new-feature",
    "permission_mode": "acceptEdits",
    "hook_event_name": "PreToolUse",
    "tool_name": "Write",
    "tool_input": {
        "file_path": "/repo/worktrees/feat/new-feature/src/component.tsx",
        "content": "export const Component = () => {}"
    }
}
EOF
)

# --- Execution ---
# Pipe the JSON payload to the standard input of the Python hook script.
# The script is executed using 'uv run'.
# Using "$PAYLOAD" in quotes is important to preserve the multi-line formatting.
echo "$PAYLOAD" | uv run "$HOOK_SCRIPT_PATH" --hook "$HOOK_NAME"
echo
