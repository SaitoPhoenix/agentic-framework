#!/usr/bin/env python3
"""
Configuration Loader - Load and validate worktree permissions configuration
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class AlwaysDenyRule(BaseModel):
    """Always deny rule with pattern and reason"""
    pattern: str
    reason: str


class GlobalConfig(BaseModel):
    """Global configuration settings"""
    enabled: bool = True
    default_permission: str = Field(default="ask")
    log_permissions: bool = True
    enforce_boundaries: bool = True
    always_allow: List[str] = Field(default_factory=list)
    always_deny: List[Any] = Field(default_factory=list)  # Can be string or dict

    @field_validator('default_permission')
    @classmethod
    def normalize_permission(cls, v: str) -> str:
        """Normalize permission to lowercase"""
        v_lower = v.lower()
        if v_lower not in {"allow", "ask", "deny", "ignore"}:
            raise ValueError(f"Invalid permission '{v}'. Must be one of: allow, ask, deny, ignore")
        return v_lower

    @field_validator('always_deny')
    @classmethod
    def normalize_always_deny(cls, v: List[Any]) -> List[AlwaysDenyRule]:
        """
        Normalize always_deny to list of AlwaysDenyRule objects.
        Supports both old format (strings) and new format (dict with pattern and reason).
        """
        rules = []
        for item in v:
            if isinstance(item, str):
                # Old format: just a pattern string, use default reason
                rules.append(AlwaysDenyRule(
                    pattern=item,
                    reason="Tool denied by always_deny rule"
                ))
            elif isinstance(item, dict):
                # New format: dict with pattern and reason
                if 'pattern' not in item:
                    raise ValueError("always_deny dict must have 'pattern' field")
                rules.append(AlwaysDenyRule(
                    pattern=item['pattern'],
                    reason=item.get('reason', "Tool denied by always_deny rule")
                ))
            else:
                raise ValueError(f"always_deny items must be strings or dicts, got {type(item)}")
        return rules


class MainWorktreeConfig(BaseModel):
    """Main worktree configuration"""
    enabled: bool = False
    permissions: Dict[str, str] = Field(default_factory=dict)

    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate and normalize permission values to lowercase"""
        valid_permissions = {"allow", "ask", "deny", "ignore"}
        normalized = {}
        for tool, perm in v.items():
            perm_lower = perm.lower()
            if perm_lower not in valid_permissions:
                raise ValueError(f"Invalid permission '{perm}' for tool '{tool}'. Must be one of: {valid_permissions}")
            normalized[tool] = perm_lower
        return normalized


class BranchPermissionEntry(BaseModel):
    """Single branch permission entry"""
    branch_types: List[str]
    reason: str  # Reason for these permissions
    permissions: Dict[str, str]

    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate and normalize permission values to lowercase"""
        valid_permissions = {"allow", "ask", "deny", "ignore"}
        normalized = {}
        for tool, perm in v.items():
            perm_lower = perm.lower()
            if perm_lower not in valid_permissions:
                raise ValueError(f"Invalid permission '{perm}'. Must be one of: {valid_permissions}")
            normalized[tool] = perm_lower
        return normalized


class UnknownBranchConfig(BaseModel):
    """Configuration for unknown/unmatched branches"""
    reason: str  # Reason for these permissions
    permissions: Dict[str, str]

    @field_validator('permissions')
    @classmethod
    def validate_permissions(cls, v: Dict[str, str]) -> Dict[str, str]:
        """Validate and normalize permission values to lowercase"""
        valid_permissions = {"allow", "ask", "deny", "ignore"}
        normalized = {}
        for tool, perm in v.items():
            perm_lower = perm.lower()
            if perm_lower not in valid_permissions:
                raise ValueError(f"Invalid permission '{perm}'. Must be one of: {valid_permissions}")
            normalized[tool] = perm_lower
        return normalized


class WorktreePermissionsConfig(BaseModel):
    """Complete worktree permissions configuration"""
    global_config: GlobalConfig = Field(alias="global")
    main_worktree: MainWorktreeConfig
    branch_permissions: List[BranchPermissionEntry]
    unknown_branch: UnknownBranchConfig

    class Config:
        populate_by_name = True


def load_config(config_file: str) -> WorktreePermissionsConfig:
    """
    Load and validate worktree permissions configuration.

    Args:
        config_file: Path to worktree-permissions.yaml (relative to project root)

    Returns:
        Validated configuration object

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        ValueError: If config validation fails
    """
    from pyprojroot import here

    # Resolve config file path relative to project root
    config_path = here() / config_file

    if not config_path.exists():
        raise FileNotFoundError(f"Worktree permissions config not found: {config_path}")

    # Load YAML
    with open(config_path, 'r') as f:
        raw_config = yaml.safe_load(f)

    # Validate with Pydantic
    config = WorktreePermissionsConfig(**raw_config)

    return config


def get_permission_for_tool(
    tool_name: str,
    branch_type: Optional[str],
    config: WorktreePermissionsConfig,
    is_main_worktree: bool = False
) -> str:
    """
    Get permission level for a specific tool based on branch type.

    Args:
        tool_name: Name of the tool (e.g., "Write", "Bash(git push:*)")
        branch_type: Type extracted from branch name (e.g., "feat", "fix")
        config: Loaded configuration
        is_main_worktree: Whether this is the main worktree

    Returns:
        Permission level: "allow", "ask", "deny", or "ignore"
    """
    # Main worktree handling
    if is_main_worktree:
        if not config.main_worktree.enabled:
            return "ignore"

        # Check main worktree permissions
        if tool_name in config.main_worktree.permissions:
            return config.main_worktree.permissions[tool_name]

    # Check always_deny first
    if tool_name in config.global_config.always_deny:
        return "deny"

    # Check always_allow
    if tool_name in config.global_config.always_allow:
        return "allow"

    # Find branch type in branch_permissions
    if branch_type:
        for entry in config.branch_permissions:
            if branch_type in entry.branch_types:
                if tool_name in entry.permissions:
                    return entry.permissions[tool_name]
                # Tool not specified for this branch type, use default
                return config.global_config.default_permission

    # Branch type not found, use unknown_branch config
    if tool_name in config.unknown_branch.permissions:
        return config.unknown_branch.permissions[tool_name]

    # Tool not specified anywhere, use default
    return config.global_config.default_permission


def match_tool_pattern(tool_name: str, tool_input: Dict[str, Any], pattern: str) -> bool:
    """
    Check if a tool matches a permission pattern.

    Patterns:
    - Exact match: "Write" matches tool_name "Write"
    - Bash pattern: "Bash(git push:*)" matches Bash tool with command starting with "git push"
    - Generic: "Bash" matches any Bash command

    Args:
        tool_name: Name of the tool being called
        tool_input: Tool input parameters
        pattern: Permission pattern to match

    Returns:
        True if tool matches pattern
    """
    # Exact match
    if pattern == tool_name:
        return True

    # Bash pattern matching: Bash(command:*)
    if pattern.startswith("Bash(") and pattern.endswith(")"):
        if tool_name != "Bash":
            return False

        # Extract command pattern
        cmd_pattern = pattern[5:-1]  # Remove "Bash(" and ")"

        if cmd_pattern.endswith(":*"):
            cmd_prefix = cmd_pattern[:-2]  # Remove ":*"
            actual_command = tool_input.get("command", "")
            return actual_command.startswith(cmd_prefix)
        else:
            # Exact command match
            actual_command = tool_input.get("command", "")
            return actual_command == cmd_pattern

    # Generic tool match (lowest priority)
    if pattern == tool_name:
        return True

    return False
