#!/usr/bin/env python3
"""
Migrate security guard test payloads to universal test format.

This script converts old-style test payloads (just hook input) to the new
universal format with metadata including test_id, category, priority, and
expected validation rules.
"""

import json
from pathlib import Path
from pyprojroot import here


# Category and priority mapping based on filename patterns
CATEGORY_MAPPING = {
    'deny_': 'security_deny',
    'ask_': 'security_ask',
    'whitelist_': 'security_allow',
    'edge_': 'edge_cases',
    'future_': 'future',
}

PRIORITY_MAPPING = {
    'security_deny': 'critical',
    'security_ask': 'high',
    'security_allow': 'high',
    'edge_cases': 'critical',
    'future': 'low',
}


# Expected validation rules based on test patterns
VALIDATION_RULES = {
    # Deny patterns
    'deny_env_file': {
        'permissionDecision': 'deny',
        'reason_regex': r'Access to \.env files.*prohibited'
    },
    'deny_env_subdirectory': {
        'permissionDecision': 'deny',
        'reason_regex': r'Access to \.env files.*prohibited'
    },
    'deny_env_uppercase': {
        'permissionDecision': 'deny',
        'reason_regex': r'Access to \.env files.*prohibited'
    },
    'deny_secrets_json': {
        'permissionDecision': 'deny',
        'reason_regex': r'Secrets file access is blocked'
    },
    'deny_secrets_yaml': {
        'permissionDecision': 'deny',
        'reason_regex': r'Secrets file access is blocked'
    },
    'deny_credentials_json': {
        'permissionDecision': 'deny',
        'reason_regex': r'Credentials file access is blocked'
    },
    'deny_aws_credentials': {
        'permissionDecision': 'deny',
        'reason_regex': r'AWS credentials access is blocked'
    },
    'deny_aws_config': {
        'permissionDecision': 'deny',
        'reason_regex': r'AWS config access is blocked'
    },
    'deny_ssh_id_rsa': {
        'permissionDecision': 'deny',
        'reason_regex': r'SSH private key access is blocked'
    },
    'deny_ssh_id_ed25519': {
        'permissionDecision': 'deny',
        'reason_regex': r'SSH private key access is blocked'
    },
    'deny_key_file': {
        'permissionDecision': 'deny',
        'reason_regex': r'Private key file access is blocked'
    },
    'deny_pem_file': {
        'permissionDecision': 'deny',
        'reason_regex': r'PEM certificate file access is blocked'
    },
    'deny_rm_-rf_slash': {
        'permissionDecision': 'deny',
        'reason_regex': r'Dangerous rm command.*prevented for safety'
    },
    'deny_rm_-rf_dot': {
        'permissionDecision': 'deny',
        'reason_regex': r'Dangerous rm command.*prevented for safety'
    },
    'deny_rm_-Rf_tilde': {
        'permissionDecision': 'deny',
        'reason_regex': r'Dangerous rm command.*prevented for safety'
    },
    'deny_rm_-fr_home': {
        'permissionDecision': 'deny',
        'reason_regex': r'Dangerous rm command.*prevented for safety'
    },
    'deny_rm_-fR_wildcard': {
        'permissionDecision': 'deny',
        'reason_regex': r'Dangerous rm command.*prevented for safety'
    },
    'deny_rm_force_recursive': {
        'permissionDecision': 'deny',
        'reason_regex': r'Dangerous rm command.*prevented for safety'
    },
    'deny_rm_recursive_force': {
        'permissionDecision': 'deny',
        'reason_regex': r'Dangerous rm command.*prevented for safety'
    },
    'deny_sudo_command': {
        'permissionDecision': 'deny',
        'reason_regex': r'sudo commands are not allowed for security'
    },
    'deny_su_command': {
        'permissionDecision': 'deny',
        'reason_regex': r'su commands are not allowed for security'
    },

    # Ask patterns
    'ask_chmod_777': {
        'permissionDecision': 'ask',
        'reason_contains': 'world-writable'
    },
    'ask_chmod_+x': {
        'permissionDecision': 'ask',
        'reason_contains': 'executable'
    },
    'ask_git_push_-f': {
        'permissionDecision': 'ask',
        'reason_regex': r'Force push detected'
    },
    'ask_git_push_force': {
        'permissionDecision': 'ask',
        'reason_regex': r'Force push detected'
    },
    'ask_curl_pipe_bash': {
        'permissionDecision': 'ask',
        'reason_regex': r'Piping.*to shell can be dangerous'
    },
    'ask_curl_pipe_sh': {
        'permissionDecision': 'ask',
        'reason_regex': r'Piping.*to shell can be dangerous'
    },
    'ask_wget_pipe_bash': {
        'permissionDecision': 'ask',
        'reason_regex': r'Piping.*to shell can be dangerous'
    },
    'ask_wget_pipe_sh': {
        'permissionDecision': 'ask',
        'reason_regex': r'Piping.*to shell can be dangerous'
    },
    'ask_api_key_file': {
        'permissionDecision': 'ask',
        'reason_regex': r'API key file detected'
    },
    'ask_token_file': {
        'permissionDecision': 'ask',
        'reason_regex': r'Token file detected'
    },

    # Whitelist patterns
    'whitelist_echo_command': {
        'permissionDecision': 'allow',
        'reason_regex': r'echo command is whitelisted'
    },
    'whitelist_env_example': {
        'permissionDecision': 'allow',
        'reason_regex': r'Template files are safe to access'
    },
    'whitelist_env_sample': {
        'permissionDecision': 'allow',
        'reason_regex': r'Sensitive file access prevented for safety: \.env\.sample'
    },
    'whitelist_env_template': {
        'permissionDecision': 'allow',
        'reason_regex': r'Sensitive file access prevented for safety: \.env\.template'
    },

    # Edge cases - need to determine based on specific content
    'edge_chained_commands': {
        'permissionDecision': 'allow',
    },
    'edge_curl_multiline': {
        'permissionDecision': 'ask',
        'reason_regex': r'Piping.*to shell can be dangerous'
    },
    'edge_dotdot_traversal': {
        'permissionDecision': 'deny',
        'reason_regex': r'Access to \.env files.*prohibited'
    },
    'edge_nested_env': {
        'permissionDecision': 'deny',
        'reason_regex': r'Access to \.env files.*prohibited'
    },
    'edge_relative_path_env': {
        'permissionDecision': 'deny',
        'reason_regex': r'Access to \.env files.*prohibited'
    },
    'edge_rm_env_var': {
        'permissionDecision': 'allow',
    },
    'edge_rm_extra_spaces': {
        'permissionDecision': 'deny',
        'reason_regex': r'Dangerous rm command.*prevented for safety'
    },
    'edge_rm_safe_specific': {
        'permissionDecision': 'allow',
    },
    'edge_secrets_mixed_case': {
        'permissionDecision': 'allow',
    },
    'edge_subshell_rm': {
        'permissionDecision': 'allow',
        'reason_regex': r'echo command is whitelisted'
    },
    'edge_file_with_spaces': {
        'permissionDecision': 'allow',
    },
    'edge_env_uppercase': {
        'permissionDecision': 'allow',
    },

    # Future tests - not yet implemented, should allow
    'future_dd_command': {
        'permissionDecision': 'allow',
    },
    'future_etc_passwd': {
        'permissionDecision': 'allow',
    },
    'future_docker_config': {
        'permissionDecision': 'allow',
    },
    'future_gpg_key': {
        'permissionDecision': 'allow',
    },
    'future_etc_shadow': {
        'permissionDecision': 'allow',
    },
    'future_git_credentials': {
        'permissionDecision': 'allow',
    },
    'future_kube_config': {
        'permissionDecision': 'allow',
    },
    'future_mkfs_command': {
        'permissionDecision': 'allow',
    },
    'future_netrc': {
        'permissionDecision': 'allow',
    },
    'future_pgpass': {
        'permissionDecision': 'allow',
    },
    'future_npmrc': {
        'permissionDecision': 'allow',
    },
}


def get_category(filename: str) -> str:
    """Determine category from filename."""
    for prefix, category in CATEGORY_MAPPING.items():
        if filename.startswith(prefix):
            return category
    return 'uncategorized'


def get_description(filename: str, payload: dict) -> str:
    """Generate description from filename and payload."""
    test_id = filename.replace('.json', '')
    tool_name = payload.get('tool_name', 'Unknown')

    # Create human-readable description
    parts = test_id.split('_')
    action = parts[0].capitalize()

    if tool_name == 'Bash':
        command = payload.get('tool_input', {}).get('command', '')
        return f"{action}: {command}"
    elif tool_name == 'Read':
        file_path = payload.get('tool_input', {}).get('file_path', '')
        return f"{action} reading {file_path}"
    elif tool_name == 'Write':
        file_path = payload.get('tool_input', {}).get('file_path', '')
        return f"{action} writing {file_path}"
    else:
        return f"{action} {tool_name} operation"


def get_tags(filename: str, payload: dict) -> list:
    """Generate tags from filename and payload."""
    tags = []
    test_id = filename.replace('.json', '')

    # Add category-based tags
    if test_id.startswith('deny_') or test_id.startswith('ask_'):
        tags.append('security')

    if test_id.startswith('edge_'):
        tags.append('edge-case')

    if test_id.startswith('future_'):
        tags.append('future')

    # Add content-based tags
    if 'env' in test_id.lower():
        tags.append('env')
    if 'rm' in test_id:
        tags.append('rm')
    if 'chmod' in test_id:
        tags.append('chmod')
    if 'git' in test_id:
        tags.append('git')
    if 'curl' in test_id or 'wget' in test_id:
        tags.append('download')
    if 'ssh' in test_id or 'key' in test_id or 'pem' in test_id:
        tags.append('credentials')
    if 'aws' in test_id:
        tags.append('aws')
    if 'sudo' in test_id or 'su' in test_id:
        tags.append('privilege-escalation')
    if 'secrets' in test_id or 'credentials' in test_id:
        tags.append('secrets')

    return tags if tags else ['general']


def get_expected_validation(test_id: str) -> dict:
    """Get expected validation rules for a test."""
    # Remove .json extension if present
    test_id = test_id.replace('.json', '')

    # Check if we have specific rules for this test
    if test_id in VALIDATION_RULES:
        rules = VALIDATION_RULES[test_id]

        # If permission decision is 'allow' and no reason specified, expect no JSON output
        if rules['permissionDecision'] == 'allow' and 'reason_regex' not in rules and 'reason_contains' not in rules:
            return {
                'output_type': 'exitcode',
                'exit_code': 0
            }

        # Otherwise, expect JSON output
        expected = {
            'output_type': 'json',
            'json_output': {
                'hookSpecificOutput.permissionDecision': rules['permissionDecision']
            }
        }

        # Add reason validation
        if 'reason_regex' in rules:
            expected['json_output']['hookSpecificOutput.permissionDecisionReason'] = {
                'regex': rules['reason_regex']
            }
        elif 'reason_contains' in rules:
            expected['json_output']['hookSpecificOutput.permissionDecisionReason'] = {
                'contains': rules['reason_contains']
            }

        return expected

    # Default validation (should not happen if we mapped all tests)
    return {
        'output_type': 'json',
        'json_output': {
            'hookSpecificOutput.hookEventName': 'PreToolUse'
        }
    }


def migrate_payload(source_file: Path, dest_dir: Path) -> dict:
    """Migrate a single payload file to new format."""
    # Read old payload
    with open(source_file, 'r') as f:
        old_payload = json.load(f)

    # Extract test ID from filename
    test_id = source_file.stem
    category = get_category(source_file.name)
    priority = PRIORITY_MAPPING.get(category, 'medium')

    # Build new format with metadata
    new_payload = {
        'metadata': {
            'test_id': test_id,
            'hook_type': 'PreToolUse',
            'category': category,
            'description': get_description(source_file.name, old_payload),
            'tags': get_tags(source_file.name, old_payload),
            'priority': priority,
            'expected': get_expected_validation(test_id),
            'migrated_from': str(source_file.relative_to(here())),
            'created': '2025-10-07'
        },
        'payload': old_payload
    }

    return new_payload


def main():
    """Main migration function."""
    project_root = here()
    source_dir = project_root / '.claude/hooks/tasks/security_guard/test_payloads'
    dest_dir = project_root / '.claude/hooks/test/payloads/pre_tool_use'

    # Ensure destination directory exists
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Get all JSON files in source directory
    source_files = list(source_dir.glob('*.json'))
    print(f"Found {len(source_files)} test payloads to migrate")

    migrated_count = 0
    skipped_count = 0

    for source_file in sorted(source_files):
        dest_file = dest_dir / source_file.name

        # Check if already migrated (skip if exists)
        if dest_file.exists():
            print(f"⏭️  Skipping {source_file.name} (already exists)")
            skipped_count += 1
            continue

        try:
            # Migrate payload
            new_payload = migrate_payload(source_file, dest_dir)

            # Write new payload
            with open(dest_file, 'w') as f:
                json.dump(new_payload, f, indent=2)

            print(f"✅ Migrated {source_file.name}")
            migrated_count += 1

        except Exception as e:
            print(f"❌ Error migrating {source_file.name}: {e}")

    print(f"\n{'='*70}")
    print(f"Migration complete!")
    print(f"  Migrated: {migrated_count}")
    print(f"  Skipped:  {skipped_count}")
    print(f"  Total:    {len(source_files)}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
