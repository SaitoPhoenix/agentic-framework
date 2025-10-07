#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "pyyaml",
# ]
# ///

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


def start_conversation_capture(
    input_data: Dict[str, Any],
    global_config: Dict[str, Any],
    human_name: str = "Human",
    agent_name: str = "Assistant",
    pid_file_name: str = "conversation_watchdog.pid",
    episodic_path: str = ".claude/agents/memory/episodic",
    **kwargs,
) -> Optional[Dict[str, Any]]:
    """
    Start conversation capture subprocess if enabled.

    Args:
        input_data: The input data received by the hook
        global_config: Global configuration settings
        human_name: Name to use for human in conversation
        agent_name: Name to use for agent in conversation
        pid_file_name: Name of PID file to store process ID
        episodic_path: Path to episodic memory directory
        **kwargs: Additional configuration parameters (unused)

    Returns:
        Optional dict with systemMessage if verbose logging is enabled
    """
    try:
        verbose_logging = global_config.get("verbose_logging", False)
        show_errors = global_config.get("show_errors", False)
        transcript_path = input_data.get("transcript_path", "")

        if not transcript_path:
            if verbose_logging:
                return {
                    "systemMessage": "No transcript path provided, skipping conversation capture"
                }
            return None

        # Create hierarchical output file path with sequential numbering
        now = datetime.now()
        current_date = now.strftime("%y%m%d")
        year = now.strftime("%Y")
        month = now.strftime("%m")

        output_dir = Path(episodic_path) / year / month
        output_dir.mkdir(parents=True, exist_ok=True)

        # Find the next sequential number for files with current_date prefix
        prefix = f"{current_date}_EP_"
        existing_files = list(output_dir.glob(f"{prefix}*.json"))

        if existing_files:
            # Extract sequence numbers and find the highest
            seq_numbers = []
            for file in existing_files:
                name = file.stem  # filename without extension
                if name.startswith(prefix):
                    try:
                        # Extract sequence number after the prefix
                        seq_part = name[len(prefix) :]
                        seq_numbers.append(int(seq_part))
                    except ValueError:
                        # Skip files that don't follow the expected format
                        continue

            next_seq = max(seq_numbers) + 1 if seq_numbers else 1
        else:
            next_seq = 1

        output_file = output_dir / f"{current_date}_EP_{next_seq}.json"

        pid_dir = Path(".claude/hooks/pid") / input_data.get("session_id", "")
        pid_dir.mkdir(parents=True, exist_ok=True)
        pid_file = pid_dir / pid_file_name

        # Build command for conversation_watchdog.py
        script_dir = Path(__file__).parent
        watchdog_script = script_dir / "conversation_watchdog.py"

        if not watchdog_script.exists():
            if verbose_logging or show_errors:
                return {
                    "systemMessage": f"Conversation watchdog script not found at {watchdog_script}"
                }
            return None

        # Build command arguments
        cmd = [
            "uv",
            "run",
            str(watchdog_script),
            f"--human={human_name}",
            f"--agent={agent_name}",
            str(transcript_path),  # input_file
            str(output_file),  # output_file
        ]

        # Start subprocess in non-blocking mode
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # Create new process group
        )

        # Store PID for cleanup
        with open(pid_file, "w") as f:
            f.write(str(process.pid))

        return {
            "systemMessage": f"Started conversation capture subprocess (PID: {process.pid}).\nOutput will be written to: {output_file}"
        }

    except Exception as e:
        if global_config.get("show_errors", True):
            return {"systemMessage": f"Failed to start conversation capture: {e}"}
        return None
