# Worktree Permissions Task

Manage tool permissions based on git worktree context and branch type.

## Overview

The Worktree Permissions task provides fine-grained control over which Claude Code tools can be used based on:

1. **Worktree context**: Main working tree vs. linked worktrees
2. **Branch type**: Extracted from branch naming convention (TYPE/name)
3. **Path boundaries**: Prevent operations outside the worktree directory

This enables safer isolated development in git worktrees by restricting tool usage based on the purpose of the branch.

## How It Works

### Detection Flow

1. **Check current working directory** (`cwd` from hook input)
2. **List all git worktrees** using `git worktree list --porcelain`
3. **Find matching worktree** by checking if `cwd` starts with any worktree path
4. **Extract branch information**:
   - Branch name: `feat/new-feature`
   - Branch type: `feat`
5. **Apply permissions** based on branch type and configuration

### Permission Decision Types

- **ignore**: Pass through, don't send any permission decision (task has no opinion)
- **allow**: Explicitly allow the tool (send hookSpecificOutput with "allow")
- **ask**: Require user confirmation before executing
- **deny**: Block the operation completely

### Execution Order

The worktree_permissions task runs **before** security_guard in the pre_tool_use hook:

1. **worktree_permissions**: Check tool-level permissions based on worktree/branch
2. **security_guard**: Check file/command-level security rules
3. **log_hook**: Log the hook event

This layered approach provides both coarse-grained (worktree) and fine-grained (security) controls.

## Special Features

### 1. cd Command Boundary Enforcement

The `cd` command receives **special handling** that overrides all other permissions:

- **ALWAYS allowed** if target directory is within worktree boundary
- **ALWAYS denied** if target directory is outside worktree boundary
- This enforcement happens regardless of branch type or permission configuration

**Purpose**: Maintain isolation and prevent accidental cross-worktree operations.

**Example**:
```bash
# Inside worktree at /repo/worktrees/feat-new-ui
cd src/components/     # ✅ Allowed (within worktree)
cd ../..               # ❌ Denied (exits worktree boundary)
cd /repo/main          # ❌ Denied (different worktree)
```

### 2. Read Tool Exception

The `Read` tool is **always allowed to read files outside the worktree**:

- Rationale: Development often requires reading files from other parts of the codebase
- Example: Reading shared configuration, library code, or documentation
- Security rules still apply (Read tool is read-only anyway)

### 3. Multiple Command Handling

For `Bash` tools with multiple commands separated by `&&`, `||`, `|`, or `;`:

1. **Split** the command into individual commands
2. **Check permission** for each command separately
3. **Return most restrictive** permission

**Permission precedence**: `deny` > `ask` > `allow` > `ignore`

**Example**:
```bash
git add . && git commit && git push

# Checks:
# - "git add ." → allow
# - "git commit" → allow
# - "git push" → ask

# Result: ask (most restrictive)
```

### 4. Subshell Handling

Subshells (`$(...)` and backticks) are **treated as single units**:

```bash
echo $(date) && ls
# Checks:
# - "echo $(date)" → as one command
# - "ls" → separate command
```

### 5. Quote Handling

Command splitting **respects quotes** (single and double):

```bash
git commit -m "feat: add && test" && git push
# Correctly splits as:
# - git commit -m "feat: add && test"
# - git push
# (Does not split inside the quoted message)
```

## Configuration

See `.claude/hooks/config/worktree-permissions.yaml` for full configuration.

### Branch Type Naming Convention

Branches must follow the pattern: `TYPE/name`

**Supported types**:
- `feat`: Feature development
- `fix`: Bug fixes
- `hotfix`: Urgent production fixes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Testing code
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `build`: Build system changes
- `ci`: CI/CD pipeline changes
- `security`: Security-related changes
- `exp`: Experimental branches

### Example Configuration

```yaml
branch_permissions:
  # Feature branches: feat/*
  - branch_types: [feat]
    permissions:
      "Write": Allow
      "Edit": Allow
      "Bash(git push:*)": Ask
      "WebFetch": Ask

  # Bug fix branches: fix/*, hotfix/*
  - branch_types: [fix, hotfix]
    permissions:
      "Write": Allow
      "Edit": Allow
      "Bash(git push:*)": Ask
      "WebFetch": Deny  # No external fetches for fixes
```

### Tool Pattern Matching

Patterns can be:

1. **Exact tool match**: `"Write"` → matches Write tool only
2. **Bash command prefix**: `"Bash(git push:*)"` → matches any git push command
3. **Generic tool**: `"Bash"` → matches any Bash command (lowest priority)

## Main Worktree Permissions

You can optionally override Claude Code's default permissions for the main working tree:

```yaml
main_worktree:
  enabled: true  # Set to true to apply these permissions
  permissions:
    "Write": Ask
    "Bash(git push:*)": Ask
```

When `enabled: false` (default), the main worktree uses standard Claude Code permissions.

## Path Boundary Enforcement

When `enforce_boundaries: true` (default), the task validates that file operations stay within the worktree:

**Checked tools**:
- `Write`, `Edit`, `MultiEdit`, `NotebookEdit`: Check `file_path` parameter
- `Bash`: Special handling for `cd` command

**Exceptions**:
- `Read` tool: Always allowed to read outside worktree
- Main worktree: Boundary enforcement only applies to linked worktrees

**Example**:
```python
# In worktree at /repo/worktrees/feat-branch
Write(file_path="/repo/worktrees/feat-branch/src/file.py")  # ✅ Allowed
Write(file_path="/repo/main/src/file.py")  # ❌ Denied (outside worktree)
Read(file_path="/repo/main/README.md")  # ✅ Allowed (Read exception)
```

## Module Structure

```
worktree_permissions/
├── __init__.py           # Package initialization
├── main.py               # Entry point: check_permissions()
├── config_loader.py      # Load and validate YAML config
├── detector.py           # Detect worktree context and branch type
├── permission_checker.py # Check tool permissions
├── path_validator.py     # Validate path boundaries
├── command_splitter.py   # Split Bash commands by separators
└── README.md            # This documentation
```

## Usage in hooks_config.yaml

```yaml
pre_tool_use:
  worktree_permissions:
    enabled: true
    module: "worktree_permissions.main"
    function: "check_permissions"
    config:
      config_file: ".claude/hooks/config/worktree-permissions.yaml"
```

## Error Handling

The task follows a **fail-open** philosophy:

- If git commands fail → pass through (allow operation)
- If configuration is invalid → pass through
- If any unexpected error occurs → pass through

**Rationale**: Never block legitimate operations due to task bugs or environmental issues.

Errors are logged if `show_errors: true` in global config.

## Testing

Test the worktree permissions task using the hook test framework:

```bash
uv run .claude/hooks/test/test_runner.py --hook pre_tool_use --filter worktree
```

Test payloads are in `.claude/hooks/test/payloads/pre_tool_use/worktree_*.json`

## Examples

### Example 1: Feature Branch Development

**Context**:
- Worktree: `/repo/worktrees/feat-new-ui`
- Branch: `feat/new-ui`
- Branch type: `feat`

**Permissions** (from config):
```yaml
- branch_types: [feat]
  permissions:
    "Write": Allow
    "Edit": Allow
    "Bash(git push:*)": Ask
```

**Tool calls**:
```python
Write(file_path="src/components/Button.tsx")  # ✅ Allow
Edit(file_path="src/App.tsx")                  # ✅ Allow
Bash(command="git push")                        # ⚠️  Ask
Bash(command="cd ../../main")                   # ❌ Deny (boundary)
```

### Example 2: Test Branch

**Context**:
- Worktree: `/repo/worktrees/test-integration`
- Branch: `test/integration`
- Branch type: `test`

**Permissions**:
```yaml
- branch_types: [test]
  permissions:
    "Write": Ask
    "Bash(git commit:*)": Deny
    "Bash(uv run pytest:*)": Allow
```

**Tool calls**:
```python
Write(file_path="tests/test_api.py")           # ⚠️  Ask
Bash(command="uv run pytest tests/")           # ✅ Allow
Bash(command="git commit -m 'test'")           # ❌ Deny
```

### Example 3: Main Worktree (Disabled)

**Context**:
- Worktree: `/repo` (main)
- Branch: `main`
- Config: `main_worktree.enabled: false`

**Result**: All tools **ignored** (pass through to security_guard)

### Example 4: Multiple Commands

**Context**:
- Branch type: `fix`
- Command: `git add . && git commit -m 'fix' && git push`

**Permission check**:
```
Split into:
1. "git add ." → Allow
2. "git commit -m 'fix'" → Allow
3. "git push" → Ask

Most restrictive: Ask
Result: ⚠️ Ask user for confirmation
```

## Troubleshooting

### Issue: Permissions not applying

**Check**:
1. Is `global.enabled: true` in config?
2. Is the task enabled in `hooks_config.yaml`?
3. Are you in a git worktree? Run `git worktree list`
4. Does your branch name match `TYPE/name` pattern?

### Issue: cd command always denied

**Check**:
- Are you trying to cd outside the worktree boundary?
- Remember: cd is **always** denied when exiting the worktree, regardless of permissions

### Issue: Read tool blocked

**Check**:
- Read should never be blocked by boundary enforcement
- Check if it's in `always_deny` list
- Check if branch-specific permissions deny it

### Enable verbose logging

In `.claude/hooks/config/hooks_config.yaml`:

```yaml
global:
  verbose_logging: true
  show_errors: true
```

This will show detailed permission decisions in the system messages.

## Design Philosophy

1. **Isolation**: Keep worktree operations contained within their boundaries
2. **Safety**: Prevent accidental cross-worktree modifications
3. **Flexibility**: Allow customization per branch type
4. **Fail-open**: Never block operations due to bugs or errors
5. **Layered security**: Work alongside security_guard for comprehensive protection
6. **Developer experience**: Provide clear, actionable error messages

## Future Enhancements

Potential improvements (documented as tests in future test payloads):

1. **Bash file path extraction**: Parse Bash commands to extract file arguments and validate boundaries
2. **Worktree-specific overrides**: Allow per-worktree custom permissions (not just by branch type)
3. **Time-based permissions**: Different permissions during working hours vs. off-hours
4. **User-based permissions**: Different permissions for different developers
5. **Remote branch detection**: Adjust permissions based on whether branch is pushed to remote

## Related Documentation

- **Security Guard Task**: `.claude/hooks/tasks/security_guard/README.md`
- **Hooks Configuration**: `.claude/hooks/config/README.md`
- **Hook Test Framework**: `.claude/hooks/test/README.md`
- **Claude Code Hooks**: https://docs.claude.com/en/docs/claude-code/hooks
