# Universal Hook Test Runner

A comprehensive testing framework for Claude Code hooks that supports all hook types with unified metadata and validation.

## Features

✅ **Universal** - Tests all 9 hook types (PreToolUse, PostToolUse, UserPromptSubmit, etc.)
✅ **Flexible Validation** - Supports exit codes, JSON output, regex, contains, exact matches
✅ **Rich Metadata** - Category, tags, priority, descriptions for each test
✅ **Powerful Filtering** - Filter by hook type, category, tag, priority, or pattern
✅ **Parallel Execution** - Fast test execution with configurable workers
✅ **Clear Reporting** - Console summaries with pass/fail breakdown

## Quick Start

### Run All Tests
```bash
uv run test_runner.py
```

### Run Tests for Specific Hook
```bash
uv run test_runner.py --hook-type PreToolUse
```

### Run by Category/Priority/Tag
```bash
uv run test_runner.py --category security_deny
uv run test_runner.py --priority critical
uv run test_runner.py --tag security
```

### List Tests Without Running
```bash
uv run test_runner.py --list
```

### Verbose Output
```bash
uv run test_runner.py --verbose
```

### Baseline & Regression Detection

Save current test results as baseline:
```bash
uv run test_runner.py --save-baseline
```

Check for regressions against baseline:
```bash
uv run test_runner.py --check-regression
```

Combined: run tests, save baseline, and check regressions:
```bash
uv run test_runner.py --save-baseline --check-regression
```

## Test Payload Format

### Full Format (with metadata)
```json
{
  "metadata": {
    "test_id": "deny_env_file",
    "hook_type": "PreToolUse",
    "category": "security_deny",
    "description": "Test blocking .env file access",
    "tags": ["security", "env"],
    "priority": "critical",
    "expected": {
      "output_type": "json",
      "json_output": {
        "hookSpecificOutput.permissionDecision": "deny",
        "hookSpecificOutput.permissionDecisionReason": {
          "regex": "Access to \\.env files.*prohibited"
        }
      }
    }
  },
  "payload": {
    "session_id": "test-123",
    "hook_event_name": "PreToolUse",
    "tool_name": "Read",
    "tool_input": {
      "file_path": "/path/.env"
    }
  }
}
```

### Simple Format (backward compatible)
```json
{
  "session_id": "test-123",
  "hook_event_name": "PreToolUse",
  "tool_name": "Read",
  "tool_input": {
    "file_path": "/path/.env"
  }
}
```

## Validation Options

### JSON Output Validation
```json
"expected": {
  "output_type": "json",
  "json_output": {
    "field.path": "exact value",
    "other.field": {
      "exact": "exact string"
    },
    "another.field": {
      "contains": "substring"
    },
    "regex.field": {
      "regex": "pattern.*here"
    }
  }
}
```

### Exit Code Validation
```json
"expected": {
  "output_type": "exitcode",
  "exit_code": 0,
  "stdout_pattern": {
    "contains": "Success"
  },
  "stderr_pattern": {
    "regex": "Error.*occurred"
  }
}
```

## Categories

- `security_deny` - Operations denied by security rules
- `security_ask` - Operations requiring confirmation
- `security_allow` - Explicitly allowed operations
- `validation` - Validation checks
- `notification` - Notification tests
- `transformation` - Data transformation tests
- `edge_cases` - Edge cases and bypass tests
- `future` - Tests for unimplemented features

## Priority Levels

- `critical` - Must pass, critical security/functionality
- `high` - Important tests
- `medium` - Standard tests
- `low` - Nice-to-have tests

## Directory Structure

```
.claude/hooks/test/
├── test_runner.py         # Main test runner
├── test_config.yaml       # Configuration
├── README.md             # This file
├── payloads/             # Test payloads by hook type
│   ├── pre_tool_use/
│   ├── post_tool_use/
│   ├── user_prompt_submit/
│   └── ...
└── reports/              # Test reports (future)
```

## Regression Detection

The test runner supports baseline comparison for detecting regressions:

**Baseline Storage:**
- Baseline saved to `.claude/hooks/test/reports/baseline.json`
- Contains test results (pass/fail/error) for each test
- Includes category, priority, and hook type metadata

**Regression Detection:**
- Compares current run against baseline
- Reports new failures (regressions)
- Reports new passes (improvements)
- Reports tests still failing
- Tracks new/missing tests

**Exit Codes:**
- `0`: All tests passed
- `1`: General test failures
- `2`: Regression detected (test that was passing now fails)
- `3`: Critical priority test failure
- `4`: High priority test failure

**CI/CD Configuration:**
Configure in `test_config.yaml`:
```yaml
ci:
  fail_on_regression: true
  fail_on_critical_failure: true
  fail_on_high_priority_failure: true
```

## CI/CD Integration

The test runner integrates with CI/CD pipelines:

- **GitHub Actions workflow** at `.github/workflows/hook-tests.yml`
- **Automatic testing** on PRs and commits
- **Test result comments** on pull requests
- **GitHub annotations** for failed tests
- **Matrix strategy** for parallel hook type testing

See [CI_CD.md](CI_CD.md) for complete documentation.

## Examples

See `payloads/pre_tool_use/example_*.json` for comprehensive examples demonstrating:
- Regex pattern matching
- Contains matching
- Exact matching
- Nested field validation
- Full metadata usage
