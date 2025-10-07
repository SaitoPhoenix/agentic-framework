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
from typing import Dict, Any, Optional


def cleanup_subprocesses(
    input_data: Dict[str, Any], global_config: Dict[str, Any], **kwargs
) -> Optional[Dict[str, Any]]:
    """
    Clean up running subprocesses for the current session by reading PIDs from the session-specific directory.

    Args:
        input_data: The input data received by the hook
        global_config: Global configuration settings
        **kwargs: Additional configuration parameters (unused)

    Returns:
        Optional dict with systemMessage if verbose logging is enabled
    """
    try:
        verbose_logging = global_config.get("verbose_logging", False)
        show_errors = global_config.get("show_errors", False)
        session_id = input_data.get("session_id", "")

        # Look for session-specific PID directory
        session_pid_dir = Path(".claude/hooks/pid") / session_id
        if not session_pid_dir.exists():
            if verbose_logging:
                return {"systemMessage": f"No PID directory found for session {session_id}"}
            return None

        messages = []
        terminated_count = 0
        error_count = 0

        # Process all PID files in the session directory
        for pid_file in session_pid_dir.glob("*.pid"):
            try:
                with open(pid_file, "r") as f:
                    pid = int(f.read().strip())

                # Check if process exists and kill it
                try:
                    # Send SIGTERM first (graceful shutdown)
                    os.kill(pid, signal.SIGTERM)
                    terminated_count += 1
                    if verbose_logging:
                        messages.append(f"Terminated subprocess PID {pid}")
                except ProcessLookupError:
                    # Process doesn't exist anymore
                    if verbose_logging:
                        messages.append(f"PID {pid} already terminated")
                except PermissionError:
                    # Can't kill process (may be owned by different user)
                    error_count += 1
                    if show_errors:
                        messages.append(f"Permission denied for PID {pid}")

                # Remove the PID file
                pid_file.unlink()

            except (ValueError, IOError) as e:
                # Invalid PID file or read error
                error_count += 1
                if show_errors:
                    messages.append(f"Error processing PID file {pid_file.name}: {e}")
                # Remove invalid PID file
                try:
                    pid_file.unlink()
                except:
                    pass

        # Clean up empty session PID directory
        try:
            if session_pid_dir.exists() and not any(session_pid_dir.iterdir()):
                session_pid_dir.rmdir()
                if verbose_logging:
                    messages.append(f"Removed empty PID directory for session {session_id}")
        except:
            pass

        # Return summary if verbose logging or if there were errors
        if verbose_logging or (error_count > 0 and show_errors):
            summary = f"Cleanup complete: {terminated_count} process(es) terminated"
            if error_count > 0:
                summary += f", {error_count} error(s)"
            if messages:
                return {"systemMessage": f"{summary}\n" + "\n".join(messages)}
            return {"systemMessage": summary}

        return None

    except Exception as e:
        if global_config.get("show_errors", False):
            return {"systemMessage": f"Error during subprocess cleanup: {e}"}
        return None
