#!/usr/bin/env python3
"""
Rule Loader - Load and parse security-rules.yaml
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pyprojroot import here


def load_security_rules(rules_file: str) -> Dict[str, Any]:
    """
    Load security rules from YAML file.

    Args:
        rules_file: Path to security-rules.yaml (relative to project root)

    Returns:
        Dictionary containing security rules, or empty dict if file doesn't exist

    Raises:
        yaml.YAMLError: If YAML parsing fails
    """
    try:
        rules_path = here() / rules_file

        if not rules_path.exists():
            return {}

        with open(rules_path, "r") as f:
            rules = yaml.safe_load(f) or {}
            return rules

    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse security rules: {e}")
    except Exception as e:
        raise Exception(f"Failed to load security rules: {e}")


def get_rules_by_permission(
    rules: Dict[str, Any], list_type: str, permission: str
) -> Dict[str, Any]:
    """
    Extract rules for a specific permission level from whitelist or blacklist.

    Args:
        rules: Full security rules dictionary
        list_type: "whitelist" or "blacklist"
        permission: "allow", "ask", or "deny"

    Returns:
        Dictionary with 'files' and 'commands' lists for that permission level
    """
    rule_list = rules.get(list_type, {})
    permission_rules = rule_list.get(permission, {})

    return {
        "files": permission_rules.get("files", []),
        "commands": permission_rules.get("commands", []),
    }
