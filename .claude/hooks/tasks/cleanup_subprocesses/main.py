#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "pyyaml",
# ]
# ///

import os
import sys
import signal
from pathlib import Path


def cleanup_subprocesses(input_data, **kwargs):
    """Clean up running subprocesses for the current session by reading PIDs from the session-specific directory."""
    try:
        session_id = input_data.get("session_id", "")
        # Look for session-specific PID directory
        session_pid_dir = Path(".claude/hooks/pid") / session_id
        if not session_pid_dir.exists():
            return

        # Process all PID files in the session directory
        for pid_file in session_pid_dir.glob("*.pid"):
            try:
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())

                # Check if process exists and kill it
                try:
                    # Send SIGTERM first (graceful shutdown)
                    os.kill(pid, signal.SIGTERM)
                    print(
                        f"Terminated subprocess with PID: {pid} for session {session_id}"
                    )
                except ProcessLookupError:
                    # Process doesn't exist anymore
                    pass
                except PermissionError:
                    # Can't kill process (may be owned by different user)
                    print(
                        f"Permission denied when trying to kill PID: {pid}",
                        file=sys.stderr,
                    )

                # Remove the PID file
                pid_file.unlink()

            except (ValueError, IOError) as e:
                # Invalid PID file or read error
                print(f"Error processing PID file {pid_file}: {e}", file=sys.stderr)
                # Remove invalid PID file
                try:
                    pid_file.unlink()
                except:
                    pass

        # Clean up empty session PID directory
        try:
            if session_pid_dir.exists() and not any(session_pid_dir.iterdir()):
                session_pid_dir.rmdir()
                print(f"Removed empty session PID directory for session {session_id}")
        except:
            pass

    except Exception as e:
        print(
            f"Error during subprocess cleanup for session {session_id}: {e}",
            file=sys.stderr,
        )
