#!/usr/bin/env python3
"""
Command Splitter - Split Bash commands by separators while respecting quotes and subshells
"""

import re
from typing import List


def split_bash_command(command: str) -> List[str]:
    """
    Split a Bash command by common separators while respecting quotes and subshells.

    Separators: &&, ||, |, ;
    Handles:
    - Single quotes: 'text'
    - Double quotes: "text"
    - Subshells: $(...) and `...`
    - Does not split inside quotes or subshells

    Args:
        command: Bash command string

    Returns:
        List of individual command strings

    Examples:
        "git add . && git commit" -> ["git add .", "git commit"]
        "cat 'file.txt' | grep 'pattern'" -> ["cat 'file.txt'", "grep 'pattern'"]
        "echo $(date) && ls" -> ["echo $(date)", "ls"]
    """
    commands = []
    current_cmd = []
    i = 0
    in_single_quote = False
    in_double_quote = False
    in_subshell_paren = 0  # Track $(...) nesting level
    in_subshell_backtick = False

    while i < len(command):
        char = command[i]

        # Handle single quotes
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            current_cmd.append(char)
            i += 1
            continue

        # Handle double quotes
        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            current_cmd.append(char)
            i += 1
            continue

        # Handle backtick subshells
        if char == '`' and not in_single_quote and not in_double_quote:
            in_subshell_backtick = not in_subshell_backtick
            current_cmd.append(char)
            i += 1
            continue

        # Handle $(...) subshells
        if char == '$' and i + 1 < len(command) and command[i + 1] == '(' and not in_single_quote and not in_double_quote:
            in_subshell_paren += 1
            current_cmd.append(char)
            i += 1
            continue

        if char == '(' and in_subshell_paren > 0 and not in_single_quote and not in_double_quote:
            in_subshell_paren += 1
            current_cmd.append(char)
            i += 1
            continue

        if char == ')' and in_subshell_paren > 0 and not in_single_quote and not in_double_quote:
            in_subshell_paren -= 1
            current_cmd.append(char)
            i += 1
            continue

        # Check for separators only if not in quotes or subshells
        if not in_single_quote and not in_double_quote and in_subshell_paren == 0 and not in_subshell_backtick:
            # Check for && separator
            if char == '&' and i + 1 < len(command) and command[i + 1] == '&':
                # Found separator
                cmd_text = ''.join(current_cmd).strip()
                if cmd_text:
                    commands.append(cmd_text)
                current_cmd = []
                i += 2  # Skip both &
                continue

            # Check for || separator
            if char == '|' and i + 1 < len(command) and command[i + 1] == '|':
                # Found separator
                cmd_text = ''.join(current_cmd).strip()
                if cmd_text:
                    commands.append(cmd_text)
                current_cmd = []
                i += 2  # Skip both |
                continue

            # Check for | separator (pipe)
            if char == '|':
                # Found separator
                cmd_text = ''.join(current_cmd).strip()
                if cmd_text:
                    commands.append(cmd_text)
                current_cmd = []
                i += 1
                continue

            # Check for ; separator
            if char == ';':
                # Found separator
                cmd_text = ''.join(current_cmd).strip()
                if cmd_text:
                    commands.append(cmd_text)
                current_cmd = []
                i += 1
                continue

        # Regular character, add to current command
        current_cmd.append(char)
        i += 1

    # Add final command
    cmd_text = ''.join(current_cmd).strip()
    if cmd_text:
        commands.append(cmd_text)

    return commands


def extract_cd_target(command: str) -> str | None:
    """
    Extract the target directory from a cd command.

    Args:
        command: Command string (should be a cd command)

    Returns:
        Target directory path, or None if not a cd command

    Examples:
        "cd /foo/bar" -> "/foo/bar"
        "cd ../other" -> "../other"
        "cd 'dir with spaces'" -> "dir with spaces"
        "ls -la" -> None
    """
    # Match cd command with target
    # Handles: cd, cd -P, cd -L, etc.
    match = re.match(r'^\s*cd\s+(?:-[LP]\s+)?(.+)$', command.strip())

    if not match:
        return None

    target = match.group(1).strip()

    # Remove quotes if present
    if (target.startswith('"') and target.endswith('"')) or \
       (target.startswith("'") and target.endswith("'")):
        target = target[1:-1]

    return target
