#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "pyyaml",
#     "pyprojroot",
#     "pydantic-ai-slim[openai,anthropic]",
#     "pydantic",
#     "pydantic-settings",
#     "typer",
#     "jinja2",
#     "pathspec",
# ]
# ///

import json
import sys
import argparse
import importlib

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Import configuration utilities
from utils.hooks_config import (
    load_hook_config,
    load_global_config,
)


def combine_task_responses(task_responses):
    """
    Combine multiple task responses according to the specified rules.

    Args:
        task_responses: List of tuples (task_name, task_response_dict)

    Returns:
        Combined response dictionary
    """
    combined = {}
    system_messages = []
    hook_specific_outputs = []

    for task_name, response in task_responses:
        if not isinstance(response, dict):
            continue

        # Rule: First "continue" field with value false wins, otherwise true
        if "continue" in response and not response["continue"]:
            if "continue" not in combined:
                combined["continue"] = False

        # Rule: First "suppressOutput" field with value true wins, otherwise false
        if "suppressOutput" in response and response["suppressOutput"]:
            if "suppressOutput" not in combined:
                combined["suppressOutput"] = True

        # Rule: First "stopReason" field wins
        if "stopReason" in response and "stopReason" not in combined:
            combined["stopReason"] = response["stopReason"]

        # Rule: First "decision" field with value "block" wins
        if "decision" in response and response["decision"] == "block":
            if "decision" not in combined:
                combined["decision"] = "block"
                # Rule: Get the "reason" field from the same task that has "decision" == "block"
                if "reason" in response:
                    combined["reason"] = response["reason"]

        # Rule: Collect all "systemMessage" fields to join later with task name
        if "systemMessage" in response and response["systemMessage"]:
            formatted_message = (
                f"Task: '{task_name}'\nMessage: {response['systemMessage']}"
            )
            system_messages.append(formatted_message)

        # Collect hookSpecificOutput with task name for tracking
        if "hookSpecificOutput" in response:
            hook_specific_outputs.append((task_name, response["hookSpecificOutput"]))

    # Set defaults if not set by any task
    if "continue" not in combined:
        combined["continue"] = True
    if "suppressOutput" not in combined:
        combined["suppressOutput"] = False

    # Join all system messages
    if system_messages:
        combined["systemMessage"] = "\n\n".join(system_messages)

    # Rule: For permission decisions, use the most restrictive one
    # Priority: deny > ask > allow
    if hook_specific_outputs:
        most_restrictive_output = _get_most_restrictive_permission_decision(
            hook_specific_outputs
        )
        if most_restrictive_output:
            combined["hookSpecificOutput"] = most_restrictive_output

    return combined


def _get_most_restrictive_permission_decision(hook_specific_outputs):
    """
    Get the most restrictive permission decision from multiple hookSpecificOutputs.

    For PreToolUse hooks:
    - Priority: deny > ask > allow
    - For ties (multiple tasks with same priority), the last one wins
    - Returns the most restrictive permissionDecision with its reason

    For other hook types (PostToolUse, UserPromptSubmit, SessionStart):
    - Returns the first hookSpecificOutput found

    Args:
        hook_specific_outputs: List of tuples (task_name, hookSpecificOutput_dict)

    Returns:
        Most restrictive hookSpecificOutput dict or None
    """
    if not hook_specific_outputs:
        return None

    # Check if this is a PreToolUse hook by looking for permissionDecision
    pre_tool_use_outputs = [
        (task_name, output)
        for task_name, output in hook_specific_outputs
        if isinstance(output, dict)
        and output.get("hookEventName") == "PreToolUse"
        and "permissionDecision" in output
    ]

    if pre_tool_use_outputs:
        # Handle PreToolUse permission decisions with priority
        permission_priority = {"deny": 3, "ask": 2, "allow": 1}

        most_restrictive = None
        highest_priority = 0

        for _task_name, output in pre_tool_use_outputs:
            decision = output.get("permissionDecision", "")
            priority = permission_priority.get(decision, 0)

            # Use >= to make last one win in case of ties
            if priority >= highest_priority:
                highest_priority = priority
                most_restrictive = output

        return most_restrictive

    # For non-PreToolUse hooks, return the first one
    # (original behavior: only one should exist)
    return hook_specific_outputs[0][1] if hook_specific_outputs else None


def main(hook_name):
    # Load configuration and input data
    hook_config = load_hook_config(hook_name)
    global_config = load_global_config()
    input_data = json.loads(sys.stdin.read())
    task_responses = []
    verbose_logging = global_config.get("verbose_logging", False)

    if not hook_config:
        error_response = {
            "systemMessage": f"hook_entry Failed: No {hook_name} hook in configuration.",
        }
        json.dump(error_response, sys.stdout)
        sys.exit(0)

    for task_name, task in hook_config.items():
        # Only run tasks that are explicitly enabled
        if not task.get("enabled", False):
            if verbose_logging:
                task_responses.append(
                    (task_name, {"systemMessage": "Task is disabled. Skipping."})
                )
            continue

        try:
            module_name = task["module"]
            function_name = task["function"]
            task_module = importlib.import_module(f"tasks.{module_name}")
            task_function = getattr(task_module, function_name)
            task_config = task.get("config") or {}
            task_args = {
                "input_data": input_data,
                "global_config": global_config,
                **task_config,
            }

            task_output = task_function(**task_args)

            # Collect the task response with task name
            if task_output:
                task_responses.append((task_name, task_output))

        except ModuleNotFoundError:
            if verbose_logging:
                task_responses.append(
                    (
                        task_name,
                        {"systemMessage": f"Error: Module '{module_name}' not found."},
                    )
                )
        except AttributeError:
            if verbose_logging:
                task_responses.append(
                    (
                        task_name,
                        {
                            "systemMessage": f"Error: Function '{function_name}' not found in module '{module_name}'."
                        },
                    )
                )
        except Exception as e:
            if verbose_logging:
                task_responses.append(
                    (
                        task_name,
                        {
                            "systemMessage": f"An unexpected error occurred running task '{module_name}': {e}"
                        },
                    )
                )

    # Combine all task responses
    final_response = combine_task_responses(task_responses)
    json.dump(final_response, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Determines which hook to run.")
    parser.add_argument(
        "--hook",
        type=str,
        required=True,
        help="The hook to run as configured in the hooks_config.yaml file (e.g., 'session_start', 'pre_tool_use', etc.).",
    )

    args = parser.parse_args()

    main(args.hook)
