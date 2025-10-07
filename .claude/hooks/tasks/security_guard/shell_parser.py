#!/usr/bin/env python3
"""
Shell Parser - Extract and analyze commands from shell syntax

Handles command chaining, subshells, pipes, and variable references
to detect dangerous commands hidden in complex shell constructs.
"""

import re
from typing import List, Set


def extract_all_commands(command_str: str) -> List[str]:
    """
    Extract all executable commands from a shell command string.

    Handles:
    - Command chaining: &&, ||, ;
    - Pipes: |
    - Subshells: $(...) and `...`
    - Background jobs: &

    Args:
        command_str: Shell command string

    Returns:
        List of individual command strings
    """
    commands = []

    # First, extract commands from subshells and command substitutions
    subshell_commands = extract_subshell_commands(command_str)
    commands.extend(subshell_commands)

    # Remove subshells from the main command to avoid double-processing
    cleaned_command = remove_subshells(command_str)

    # Split by command separators: &&, ||, ;, |, &
    # Use regex to split while preserving the structure
    separator_pattern = r'(\s*(?:&&|\|\||;|\||&)\s*)'
    parts = re.split(separator_pattern, cleaned_command)

    # Extract actual commands (odd indices are separators)
    for i, part in enumerate(parts):
        if i % 2 == 0 and part.strip():  # Even indices are commands
            cmd = part.strip()
            if cmd and not is_separator(cmd):
                commands.append(cmd)

    return commands


def extract_subshell_commands(command_str: str) -> List[str]:
    """
    Extract commands from subshells: $(...) and `...`

    Args:
        command_str: Shell command string

    Returns:
        List of commands found in subshells
    """
    commands = []

    # Extract from $(...) syntax
    dollar_paren_pattern = r'\$\(([^)]+)\)'
    for match in re.finditer(dollar_paren_pattern, command_str):
        subcommand = match.group(1).strip()
        if subcommand:
            # Recursively extract commands from nested subshells
            commands.extend(extract_all_commands(subcommand))

    # Extract from `...` syntax (backticks)
    backtick_pattern = r'`([^`]+)`'
    for match in re.finditer(backtick_pattern, command_str):
        subcommand = match.group(1).strip()
        if subcommand:
            # Recursively extract commands from nested backticks
            commands.extend(extract_all_commands(subcommand))

    return commands


def remove_subshells(command_str: str) -> str:
    """
    Remove subshell syntax from command string for cleaner parsing.

    Args:
        command_str: Shell command string

    Returns:
        Command string with subshells replaced by placeholder
    """
    # Replace $(...) with placeholder
    result = re.sub(r'\$\([^)]+\)', '__SUBSHELL__', command_str)

    # Replace `...` with placeholder
    result = re.sub(r'`[^`]+`', '__SUBSHELL__', result)

    return result


def is_separator(text: str) -> bool:
    """
    Check if text is a command separator.

    Args:
        text: Text to check

    Returns:
        True if text is a separator
    """
    separators = {'&&', '||', ';', '|', '&'}
    return text.strip() in separators


def contains_variable_reference(path_str: str) -> bool:
    """
    Check if a path string contains shell variable references.

    Detects:
    - $VAR
    - ${VAR}
    - ~
    - ~user

    Args:
        path_str: Path string to check

    Returns:
        True if path contains variable references
    """
    # Check for $VAR or ${VAR}
    if '$' in path_str:
        return True

    # Check for ~ or ~user
    if path_str.startswith('~'):
        return True

    # Check for environment variable patterns in middle of path
    if re.search(r'\$\{?\w+\}?', path_str):
        return True

    return False


def extract_variable_references(command_str: str) -> Set[str]:
    """
    Extract all variable references from a command string.

    Args:
        command_str: Shell command string

    Returns:
        Set of variable names referenced in the command
    """
    variables = set()

    # Match $VAR and ${VAR}
    var_pattern = r'\$\{?(\w+)\}?'
    for match in re.finditer(var_pattern, command_str):
        variables.add(match.group(1))

    # Check for ~ (HOME)
    if '~' in command_str:
        variables.add('HOME')

    return variables


def normalize_path_with_quotes(path_str: str) -> str:
    """
    Normalize a path string by removing quotes.

    Handles:
    - Double quotes: "path"
    - Single quotes: 'path'
    - Escaped spaces: path\ with\ spaces

    Args:
        path_str: Path string possibly with quotes

    Returns:
        Normalized path string
    """
    # Remove surrounding quotes
    if (path_str.startswith('"') and path_str.endswith('"')) or \
       (path_str.startswith("'") and path_str.endswith("'")):
        path_str = path_str[1:-1]

    # Handle escaped spaces
    path_str = path_str.replace('\\ ', ' ')

    return path_str


def extract_paths_from_command(command_str: str) -> List[str]:
    """
    Extract file paths from a command string.

    Handles:
    - Quoted paths with spaces: "my file.txt"
    - Unquoted paths: /path/to/file
    - Paths with variables: $HOME/file

    Args:
        command_str: Shell command string

    Returns:
        List of extracted file paths
    """
    paths = []

    # Extract quoted paths (with spaces)
    quoted_pattern = r'["\']([^"\']+)["\']'
    for match in re.finditer(quoted_pattern, command_str):
        path = match.group(1)
        if '/' in path or '.' in path:  # Likely a path
            paths.append(path)

    # Extract unquoted paths (split by whitespace, look for path-like tokens)
    # Remove quoted sections first
    unquoted = re.sub(quoted_pattern, '', command_str)
    tokens = unquoted.split()

    for token in tokens:
        # Skip flags and operators
        if token.startswith('-') or token in {'&&', '||', ';', '|', '&'}:
            continue

        # Check if token looks like a path
        if '/' in token or token.startswith('~') or token.startswith('.'):
            paths.append(token)

    return paths
