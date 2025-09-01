#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = ["pyyaml"]
# ///

import json
import sys
from pathlib import Path
from utils.hooks_config import load_hook_config, get_log_directory, should_log_to_file

def main():
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)
        
        # Only log to file if enabled in config (defaults to True for backward compatibility)
        if should_log_to_file('post_tool_use'):
            # Ensure log directory exists
            log_dir = get_log_directory()
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / 'post_tool_use.json'
            
            # Read existing log data or initialize empty list
            if log_path.exists():
                with open(log_path, 'r') as f:
                    try:
                        log_data = json.load(f)
                    except (json.JSONDecodeError, ValueError):
                        log_data = []
            else:
                log_data = []
            
            # Append new data
            log_data.append(input_data)
            
            # Write back to file with formatting
            with open(log_path, 'w') as f:
                json.dump(log_data, f, indent=2)
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Exit cleanly on any other error
        sys.exit(0)

if __name__ == '__main__':
    main()