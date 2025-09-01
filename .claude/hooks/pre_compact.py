#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from utils.hooks_config import load_hook_config, get_log_directory, should_log_to_file

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def log_pre_compact(input_data):
    """Log pre-compact event to logs directory."""
    # Only log if enabled in config
    if not should_log_to_file('pre_compact'):
        return
    
    # Use configured log directory
    log_dir = get_log_directory()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'pre_compact.json'
    
    # Read existing log data or initialize empty list
    if log_file.exists():
        with open(log_file, 'r') as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []
    
    # Append the entire input data
    log_data.append(input_data)
    
    # Write back to file with formatting
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)


def backup_transcript(transcript_path, trigger, hook_config):
    """Create a backup of the transcript before compaction."""
    try:
        if not Path(transcript_path).exists():
            return
        
        # Get backup directory from config
        log_dir = get_log_directory()
        backup_subdir = hook_config.get('backup_dir', 'transcript_backups/')
        backup_dir = log_dir / backup_subdir.rstrip('/')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp and trigger type
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_name = Path(transcript_path).stem
        backup_name = f"{session_name}_pre_compact_{trigger}_{timestamp}.jsonl"
        backup_path = backup_dir / backup_name
        
        # Copy transcript to backup
        import shutil
        shutil.copy2(transcript_path, backup_path)
        
        return str(backup_path)
    except Exception:
        return None


def main():
    try:
        # Load hook configuration
        hook_config = load_hook_config('pre_compact')
        
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Extract fields
        session_id = input_data.get('session_id', 'unknown')
        transcript_path = input_data.get('transcript_path', '')
        trigger = input_data.get('trigger', 'unknown')  # "manual" or "auto"
        custom_instructions = input_data.get('custom_instructions', '')
        
        # Log the pre-compact event
        log_pre_compact(input_data)
        
        # Create backup if enabled in config
        backup_path = None
        if hook_config.get('create_backup', True) and transcript_path:
            backup_path = backup_transcript(transcript_path, trigger, hook_config)
        
        # Provide feedback based on config
        if hook_config.get('verbose_output', False):
            if trigger == "manual":
                message = f"Preparing for manual compaction (session: {session_id[:8]}...)"
                if custom_instructions:
                    message += f"\nCustom instructions: {custom_instructions[:100]}..."
            else:  # auto
                message = f"Auto-compaction triggered due to full context window (session: {session_id[:8]}...)"
            
            if backup_path:
                message += f"\nTranscript backed up to: {backup_path}"
            
            print(message)
        
        # Success - compaction will proceed
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == '__main__':
    main()