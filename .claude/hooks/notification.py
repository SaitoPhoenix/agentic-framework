#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "pyyaml",
# ]
# ///

import json
import os
import sys
import subprocess
import random
from pathlib import Path
from utils.hooks_config import load_hook_config, load_global_config, get_subprocess_timeout, get_log_directory

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def get_tts_script_path():
    """
    Determine which TTS script to use based on available API keys.
    Priority order: ElevenLabs > OpenAI > pyttsx3
    """
    # Get current script directory and construct utils/tts path
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "utils" / "tts"
    
    # Check for ElevenLabs API key (highest priority)
    if os.getenv('ELEVENLABS_API_KEY'):
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return str(elevenlabs_script)
    
    # Check for OpenAI API key (second priority)
    if os.getenv('OPENAI_API_KEY'):
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            return str(openai_script)
    
    # Fall back to pyttsx3 (no API key required)
    pyttsx3_script = tts_dir / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        return str(pyttsx3_script)
    
    return None


def announce_notification():
    """Announce that the agent needs user input."""
    try:
        tts_script = get_tts_script_path()
        if not tts_script:
            return  # No TTS scripts available
        
        # Get engineer name if available
        engineer_name = os.getenv('ENGINEER_NAME', '').strip()
        
        # Create notification message with 30% chance to include name
        if engineer_name and random.random() < 0.3:
            notification_message = f"{engineer_name}, your agent needs your input"
        else:
            notification_message = "Your agent needs your input"
        
        # Call the TTS script with the notification message
        subprocess.run([
            "uv", "run", tts_script, notification_message
        ], 
        capture_output=True,  # Suppress output
        timeout=get_subprocess_timeout()  # Use global timeout setting
        )
        
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        # Fail silently if TTS encounters issues
        pass
    except Exception:
        # Fail silently for any other errors
        pass


def main():
    try:
        # Load configuration directly from utilities
        hook_config = load_hook_config('notification')
        global_config = load_global_config()
        
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Ensure log directory exists
        log_dir = get_log_directory()
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'notification.json'
        
        # Log to file if enabled
        if hook_config.get('log_to_file', True):
            # Read existing log data or initialize empty list
            if log_file.exists():
                with open(log_file, 'r') as f:
                    try:
                        log_data = json.load(f)
                    except (json.JSONDecodeError, ValueError):
                        log_data = []
            else:
                log_data = []
            
            # Append new data
            log_data.append(input_data)
            
            # Write back to file with formatting
            with open(log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
        
        # Handle notifications based on config
        enable_tts = hook_config.get('enable_tts', False)
        speak_all = hook_config.get('speak_all', False)
        
        # Announce notification via TTS if enabled
        # Skip TTS for generic messages unless speak_all is enabled
        if enable_tts:
            skip_generic = not speak_all and input_data.get('message') == 'Claude is waiting for your input'
            if not skip_generic:
                announce_notification()
        
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)

if __name__ == '__main__':
    main()