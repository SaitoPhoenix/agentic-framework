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


def main(hook_name):
    try:
        # Load configuration and input data
        hook_config = load_hook_config(hook_name)
        global_config = load_global_config()
        input_data = json.loads(sys.stdin.read())
        if not hook_config:
            print(f"No {hook_name} hook in configuration. Exiting.")
            sys.exit(0)

        for task_name, task in hook_config.items():
            # Only run tasks that are explicitly enabled
            if not task.get("enabled", False):
                print(f"Skipping disabled task: '{task_name}'")
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
                task_function(**task_args)

            except ModuleNotFoundError:
                print(f"Error: Module '{module_name}' not found.")
            except AttributeError:
                print(
                    f"Error: Function '{function_name}' not found in module '{module_name}'."
                )
            except Exception as e:
                print(f"An unexpected error occurred running task '{module_name}': {e}")
        # Success
        sys.exit(0)

    except json.JSONDecodeError as e:
        # Handle JSON decode errors gracefully
        try:
            verbose_errors = global_config.get("verbose_errors", False)
            if verbose_errors:
                print(f"Session end hook JSON decode error: {e}", file=sys.stderr)
        except:
            pass
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully
        try:
            verbose_errors = global_config.get("verbose_errors", False)
            if verbose_errors:
                print(f"Session end hook error: {e}", file=sys.stderr)
        except:
            pass
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
