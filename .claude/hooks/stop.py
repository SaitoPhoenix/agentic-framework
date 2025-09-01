#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "requests",
#     "pyyaml",
# ]
# ///

import json
import os
import sys
import random
import subprocess
import requests
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional

from utils.hooks_config import (
    load_hook_config,
    load_global_config,
    get_log_directory,
    should_log_to_file,
    get_subprocess_timeout,
    get_agent_name,
)


def get_completion_messages():
    """Return list of friendly completion messages."""
    return [
        "Work complete!",
        "All done!",
        "Task finished!",
        "Job complete!",
        "Ready for next task!",
    ]


def get_tts_script_path():
    """
    Determine which TTS script to use based on available API keys.
    Priority order: ElevenLabs > OpenAI > pyttsx3
    """
    # Get current script directory and construct utils/tts path
    script_dir = Path(__file__).parent
    tts_dir = script_dir / "utils" / "tts"

    # Check for ElevenLabs API key (highest priority)
    if os.getenv("ELEVENLABS_API_KEY"):
        elevenlabs_script = tts_dir / "elevenlabs_tts.py"
        if elevenlabs_script.exists():
            return str(elevenlabs_script)

    # Check for OpenAI API key (second priority)
    if os.getenv("OPENAI_API_KEY"):
        openai_script = tts_dir / "openai_tts.py"
        if openai_script.exists():
            return str(openai_script)

    # Fall back to pyttsx3 (no API key required)
    pyttsx3_script = tts_dir / "pyttsx3_tts.py"
    if pyttsx3_script.exists():
        return str(pyttsx3_script)

    return None


def get_chat_result(transcript_path):
    """
    Extract the most recent assistant message from the transcript.

    Args:
        transcript_path (str): Path to the transcript .jsonl file

    Returns:
        str: The most recent assistant message, or None if not found
    """
    if not os.path.exists(transcript_path):
        return None

    try:
        assistant_message = None
        with open(transcript_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entry = json.loads(line)
                        # Check for nested message structure (Claude Code transcript format)
                        if "message" in entry and isinstance(entry["message"], dict):
                            msg = entry["message"]
                            if msg.get("role") == "assistant" and msg.get("content"):
                                content = msg["content"]
                                # Extract text from content array
                                if isinstance(content, list):
                                    for item in content:
                                        if (
                                            isinstance(item, dict)
                                            and item.get("type") == "text"
                                        ):
                                            # Keep updating to get the last text message
                                            assistant_message = item.get("text", "")
                                elif isinstance(content, str):
                                    assistant_message = content
                    except json.JSONDecodeError:
                        pass

        return assistant_message
    except Exception:
        return None


def slack_notification(chat_result, agent_name="CLAUDE"):
    """
    Send a formatted notification to Slack.

    Args:
        chat_result (str): The message to send
        agent_name (str): Name of the agent (default: "CLAUDE")
    """
    # Get Slack webhook URL from environment
    slack_url = os.getenv("SLACK_NOTIFICATION_URL")
    if not slack_url:
        return  # No Slack URL configured

    if not chat_result:
        return  # No message to send

    try:
        # Check if message needs summarization (over 500 chars)
        if len(chat_result) > 500:
            # Use TabbyAPI to summarize the message if available
            if os.getenv("TABBYAPI_APIKEY"):
                try:
                    # Get script path
                    script_dir = Path(__file__).parent
                    tabby_script = script_dir / "utils" / "llm" / "tabbyapi.py"

                    if tabby_script.exists():
                        # Create prompt for summarization
                        summarize_prompt = f"""Summarize this assistant's response into a concise bullet-point list.
Keep only the most important points. Maximum 3-4 bullet points.
Format as: • Point one\\n• Point two\\n• Point three

Response to summarize:
{chat_result}

Summary (bullets only, no intro):"""

                        # Call TabbyAPI to summarize
                        result = subprocess.run(
                            ["uv", "run", str(tabby_script), summarize_prompt],
                            capture_output=True,
                            text=True,
                            timeout=get_subprocess_timeout(),
                        )

                        if result.returncode == 0 and result.stdout.strip():
                            message_to_send = result.stdout.strip()
                        else:
                            # Fallback to truncation if summarization fails
                            message_to_send = chat_result[:500] + "..."
                    else:
                        # Fallback to truncation if script not found
                        message_to_send = chat_result[:500] + "..."
                except Exception:
                    # Fallback to truncation if TabbyAPI fails
                    message_to_send = chat_result[:500] + "..."
            else:
                # No TabbyAPI configured, use simple truncation
                message_to_send = chat_result[:500] + "..."
        else:
            # Message is short enough, send as-is
            message_to_send = chat_result

        # Format message as [AGENT]: Message
        formatted_text = f"[{agent_name}]: {message_to_send}"

        # Create Slack payload
        payload = {"text": formatted_text}

        # Set proper headers
        headers = {"Content-type": "application/json"}

        # Send to Slack
        response = requests.post(
            slack_url, json=payload, headers=headers, timeout=get_subprocess_timeout()
        )
        response.raise_for_status()

    except requests.exceptions.RequestException:
        # Fail silently if Slack notification fails
        pass
    except Exception:
        # Fail silently for any other errors
        pass


def get_llm_completion_message():
    """
    Generate completion message using available LLM services.
    Priority order: OpenAI > Anthropic > Ollama > fallback to random message

    Returns:
        str: Generated or fallback completion message
    """
    # Get current script directory and construct utils/llm path
    script_dir = Path(__file__).parent
    llm_dir = script_dir / "utils" / "llm"

    # Try OpenAI first (highest priority)
    if os.getenv("OPENAI_API_KEY"):
        oai_script = llm_dir / "oai.py"
        if oai_script.exists():
            try:
                result = subprocess.run(
                    ["uv", "run", str(oai_script), "--completion"],
                    capture_output=True,
                    text=True,
                    timeout=get_subprocess_timeout(),
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try Anthropic second
    if os.getenv("ANTHROPIC_API_KEY"):
        anth_script = llm_dir / "anth.py"
        if anth_script.exists():
            try:
                result = subprocess.run(
                    ["uv", "run", str(anth_script), "--completion"],
                    capture_output=True,
                    text=True,
                    timeout=get_subprocess_timeout(),
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

    # Try Ollama third (local LLM)
    ollama_script = llm_dir / "ollama.py"
    if ollama_script.exists():
        try:
            result = subprocess.run(
                ["uv", "run", str(ollama_script), "--completion"],
                capture_output=True,
                text=True,
                timeout=get_subprocess_timeout(),
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

    # Fallback to random predefined message
    messages = get_completion_messages()
    return random.choice(messages)


def announce_completion():
    """Announce completion using the best available TTS service."""
    try:
        tts_script = get_tts_script_path()
        if not tts_script:
            return  # No TTS scripts available

        # Get completion message (LLM-generated or fallback)
        completion_message = get_llm_completion_message()

        # Call the TTS script with the completion message
        subprocess.run(
            ["uv", "run", tts_script, completion_message],
            capture_output=True,  # Suppress output
            timeout=get_subprocess_timeout(),
        )

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        # Fail silently if TTS encounters issues
        pass
    except Exception:
        # Fail silently for any other errors
        pass


def main():
    try:
        # Load configuration using shared utilities
        hook_config = load_hook_config("stop")
        global_config = load_global_config()
        verbose_errors = global_config.get("verbose_errors", False)

        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Extract required fields
        session_id = input_data.get("session_id", "")
        stop_hook_active = input_data.get("stop_hook_active", False)

        # Ensure log directory exists using shared utility
        log_dir = get_log_directory()
        log_dir.mkdir(exist_ok=True)
        log_path = log_dir / "stop.json"

        # Log to file if enabled using shared utility
        if should_log_to_file("stop"):
            # Read existing log data or initialize empty list
            if log_path.exists():
                try:
                    with open(log_path, "r") as f:
                        log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
            else:
                log_data = []

            # Append new data
            log_data.append(input_data)

            # Write back to file with formatting
            with open(log_path, "w") as f:
                json.dump(log_data, f, indent=2)

        # Handle chat logging if enabled
        if (
            hook_config.get("enable_chat_log", False)
            and "transcript_path" in input_data
        ):
            transcript_path = input_data["transcript_path"]
            if os.path.exists(transcript_path):
                # Read .jsonl file and convert to JSON array
                chat_data = []
                try:
                    with open(transcript_path, "r") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                try:
                                    chat_data.append(json.loads(line))
                                except json.JSONDecodeError:
                                    pass  # Skip invalid lines

                    # Write to agent-specific chat log file
                    agent_name = get_agent_name(session_id).lower()
                    agent_chats_dir = log_dir / "agent_chats"
                    agent_chats_dir.mkdir(exist_ok=True)
                    chat_file = agent_chats_dir / f"{agent_name}_chat.json"
                    with open(chat_file, "w") as f:
                        json.dump(chat_data, f, indent=2)
                except Exception:
                    pass  # Fail silently

        # Handle notifications based on config
        enable_slack = hook_config.get("enable_slack", False)
        enable_tts = hook_config.get("enable_tts", False)
        debug_mode = hook_config.get("debug_mode", False)

        if enable_slack or enable_tts:
            # Debug logging if enabled
            if debug_mode:
                debug_file = Path(log_dir) / "slack_debug.log"
                with open(debug_file, "a") as df:
                    df.write(f"\n=== Stop Hook Notify at {datetime.now()} ===\n")
                    df.write(
                        f"Transcript path provided: {'transcript_path' in input_data}\n"
                    )
                    df.write(f"Slack enabled: {enable_slack}\n")
                    df.write(f"TTS enabled: {enable_tts}\n")

            # Try to send Slack notification if enabled
            if enable_slack and "transcript_path" in input_data:
                chat_result = get_chat_result(input_data["transcript_path"])

                if debug_mode:
                    with open(debug_file, "a") as df:
                        df.write(f"Chat result extracted: {chat_result is not None}\n")
                        if chat_result:
                            df.write(f"Chat result length: {len(chat_result)}\n")
                            df.write(f"First 100 chars: {chat_result[:100]}...\n")

                if chat_result:
                    # Get agent name using shared utility
                    agent_name = get_agent_name(session_id)

                    if debug_mode:
                        with open(debug_file, "a") as df:
                            df.write(f"Agent name: {agent_name}\n")
                            df.write(f"Calling slack_notification...\n")

                    # Send Slack notification
                    slack_notification(chat_result, agent_name)

                    if debug_mode:
                        with open(debug_file, "a") as df:
                            df.write(f"slack_notification completed\n")

            # Announce via TTS if enabled
            if enable_tts:
                announce_completion()

        sys.exit(0)

    except json.JSONDecodeError as e:
        # Handle JSON decode errors gracefully
        try:
            verbose_errors = load_global_config().get("verbose_errors", False)
            if verbose_errors:
                print(f"Stop hook JSON decode error: {e}", file=sys.stderr)
        except:
            pass
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully
        try:
            verbose_errors = load_global_config().get("verbose_errors", False)
            if verbose_errors:
                print(f"Stop hook error: {e}", file=sys.stderr)
        except:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()
