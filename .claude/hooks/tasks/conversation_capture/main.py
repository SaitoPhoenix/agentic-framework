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


def start_conversation_capture(
    input_data,
    human_name="Human",
    agent_name="Assistant",
    pid_file_name="conversation_watchdog.pid",
    episodic_path=".claude/agents/memory/episodic",
    **kwargs,
):
    """Start conversation capture subprocess if enabled."""
    try:
        transcript_path = input_data.get("transcript_path", "")

        if not transcript_path:
            print(
                "No transcript path provided, skipping conversation capture",
                file=sys.stderr,
            )
            return

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
            print(
                f"Conversation watchdog script not found at {watchdog_script}",
                file=sys.stderr,
            )
            return

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

        print(f"Started conversation capture subprocess (PID: {process.pid})")
        print(f"Output will be written to: {output_file}")

    except Exception as e:
        print(f"Failed to start conversation capture: {e}", file=sys.stderr)
