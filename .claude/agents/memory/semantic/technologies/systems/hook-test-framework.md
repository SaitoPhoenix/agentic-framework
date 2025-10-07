---
name: hook-test-framework
aliases:
  - test runner
  - hook test runner
  - universal hook test runner
entity_classification: technology/system
status: active
created: 2025-10-06T00:00:00Z
last_updated: 2025-10-06T00:00:00Z
source_episodes:
  - 251006_EP_2
summary: A comprehensive testing framework for Claude Code hooks that automates test discovery, execution, validation, and reporting with support for multiple hook types and validation strategies
ambiguities: []
relationships:
  - type: is_part_of
    entity: claude-code-hooks
    description: Testing framework designed specifically for validating Claude Code hooks behavior
    role: testing component
    source: 251006_EP_2
  - type: designed_by
    entity: the-architect
    description: The Architect designed and implemented the complete test framework
    role: implementation
    source: 251006_EP_2
  - type: uses
    entity: security-guard
    description: Primary hook being tested with 57 comprehensive test cases
    role: consumer
    source: 251006_EP_2
---

## Facts

### Architecture
- Located in .claude/hooks/test/ directory [251006_EP_2]
- Consists of test_runner.py, migrate_payloads.py, and test_config.yaml [251006_EP_2]
- Supports all 9 Claude Code hook types (session_start, user_prompt_submit, pre_tool_use, post_tool_use, stop, etc.) [251006_EP_2]
- Test payloads organized by hook type in payloads/ directory structure [251006_EP_2]
- Executes tests by piping JSON payloads to hook_entry.py [251006_EP_2]

### Test Discovery
- Automatically discovers all JSON test payloads in configured directories [251006_EP_2]
- Uses pathlib.rglob() for recursive file discovery [251006_EP_2]
- Supports filtering by hook type, category, tag, priority, and pattern [251006_EP_2]
- Can list discovered tests without running them using --list flag [251006_EP_2]

### Test Execution
- Runs tests sequentially by default [251006_EP_2]
- Executes command: cat payload.json | uv run hook_entry.py --hook <type> [251006_EP_2]
- Supports verbose mode for detailed output [251006_EP_2]
- Captures both stdout and stderr from hook execution [251006_EP_2]
- Validates exit codes (0=allow, 1=ask, 2=deny) [251006_EP_2]

### Validation Strategies
- Supports multiple output_type validations: json, exitcode, text [251006_EP_2]
- JSON validation checks for expected_decision field matching [251006_EP_2]
- Supports regex pattern matching for reason messages [251006_EP_2]
- Supports contains string matching for reason messages [251006_EP_2]
- Falls back to stderr if stdout is empty for JSON output [251006_EP_2]

### Test Payload Format
- JSON format with metadata and expected_validation sections [251006_EP_2]
- Metadata includes name, hook_type, category, tags, priority, description [251006_EP_2]
- Expected validation defines output_type, expected_decision, and reason validation [251006_EP_2]
- Backward compatible with old format payloads without metadata [251006_EP_2]

### Reporting
- Console output with clear pass/fail counts [251006_EP_2]
- JSON report generation with detailed test results [251006_EP_2]
- Markdown report generation for human-readable summaries [251006_EP_2]
- Reports saved in .claude/hooks/test/reports/ directory [251006_EP_2]
- Latest report symlinked for quick access [251006_EP_2]

## Accomplishments

### Phase 1: Core Test Runner
- Implemented directory structure with .claude/hooks/test/ [251006_EP_2]
- Created test_config.yaml with all 9 hook types mapped [251006_EP_2]
- Built test discovery system with filtering capabilities [251006_EP_2]
- Implemented test execution pipeline with validation [251006_EP_2]
- Created console output with summary statistics [251006_EP_2]

### Phase 2: Enhanced Validation
- Added support for regex pattern matching in validation [251006_EP_2]
- Implemented contains string matching for reason messages [251006_EP_2]
- Added support for multiple output types (json, exitcode, text) [251006_EP_2]
- Enhanced error messages for validation failures [251006_EP_2]
- Fixed handling of empty stdout by checking stderr for JSON [251006_EP_2]

### Phase 3: Report Generation
- Implemented JSON report generation with test details [251006_EP_2]
- Created Markdown report with formatted tables and sections [251006_EP_2]
- Added timestamped reports with latest symlink [251006_EP_2]
- Included execution time and statistics in reports [251006_EP_2]

### Phase 4: Test Migration
- Created migrate_payloads.py script for automated test migration [251006_EP_2]
- Defined validation rules for all 57 security guard tests [251006_EP_2]
- Successfully migrated all tests from old to new format [251006_EP_2]
- Added comprehensive metadata including categories, tags, and priorities [251006_EP_2]
- All 57 tests passing after migration [251006_EP_2]

## Decisions

- **Test payloads organized by hook type** [251006_EP_2]
  - **Category:** Organization
  - **Status:** Final
  - **Created:** 2025-10-06
  - **Rationale:** Mirrors hook structure and makes finding tests easier
  - **Impact:** Directory structure: payloads/{hook_type}/*.json

- **Use JSON format for test payloads** [251006_EP_2]
  - **Category:** Test Format
  - **Status:** Final
  - **Created:** 2025-10-06
  - **Rationale:** Matches hook input format and supports rich metadata
  - **Impact:** All tests must be valid JSON with expected validation section

- **Support multiple validation strategies** [251006_EP_2]
  - **Category:** Validation
  - **Status:** Final
  - **Created:** 2025-10-06
  - **Rationale:** Different hooks have different output formats and validation needs
  - **Impact:** Flexible validation system supporting json, exitcode, and text output types

- **Generate both JSON and Markdown reports** [251006_EP_2]
  - **Category:** Reporting
  - **Status:** Final
  - **Created:** 2025-10-06
  - **Rationale:** JSON for programmatic use, Markdown for human readability
  - **Impact:** Dual report format with timestamped files and latest symlinks

## Patterns

### Test Coverage Strategy
- Comprehensive coverage of all security rules with 57 test cases [251006_EP_2]
- Organized into categories: whitelist, deny, ask, edge cases, future enhancements [251006_EP_2]
- Tests cover both file-based and command-based security rules [251006_EP_2]
- Edge cases test unusual inputs like uppercase filenames, spaces, path traversal [251006_EP_2]
- Future tests document potential security rules not yet implemented [251006_EP_2]

### Test Categorization
- Whitelist tests validate allowed patterns (4 tests) [251006_EP_2]
- Deny tests validate blocked operations (20 tests) [251006_EP_2]
- Ask tests validate confirmation prompts (10 tests) [251006_EP_2]
- Edge case tests validate boundary conditions (12 tests) [251006_EP_2]
- Future tests document enhancement opportunities (11 tests) [251006_EP_2]

### Migration Approach
- Automated migration with validation rules defined in code [251006_EP_2]
- Comprehensive validation rules for all test categories [251006_EP_2]
- Handles tests that currently pass through (no output) as exitcode validation [251006_EP_2]
- Enriches metadata with categories, tags, and priorities [251006_EP_2]

## Approaches

### Test Execution Model
- Sequential execution ensures predictable test order [251006_EP_2]
- Each test runs in isolation via subprocess [251006_EP_2]
- Captures complete output (stdout and stderr) for validation [251006_EP_2]
- Continue on failure to run all tests even if some fail [251006_EP_2]

### Validation Philosophy
- Multiple validation strategies for different output types [251006_EP_2]
- Flexible matching with both regex and contains options [251006_EP_2]
- Backward compatibility with old format payloads [251006_EP_2]
- Clear error messages when validation fails [251006_EP_2]

### Reporting Strategy
- Timestamped reports preserve history [251006_EP_2]
- Latest symlink provides quick access to most recent results [251006_EP_2]
- Detailed JSON for programmatic analysis [251006_EP_2]
- Human-readable Markdown with formatted tables [251006_EP_2]

## Requirements

- **uv must be used for running Python scripts** [251006_EP_2]
  - **Category:** Execution Environment
  - **Priority:** Critical
  - **Status:** Active
  - **Details:** All scripts must be run with `uv run` instead of python3 or python
  - **Created:** 2025-10-06

- **Test payloads must be valid JSON** [251006_EP_2]
  - **Category:** Test Format
  - **Priority:** High
  - **Status:** Active
  - **Details:** All test files must parse as valid JSON and include expected_validation section
  - **Created:** 2025-10-06

## Constraints

- **Tests run sequentially only** [251006_EP_2]
  - **Category:** Execution Model
  - **Status:** Active
  - **Scope:** Test runner execution
  - **Reason:** Simplifies implementation and ensures predictable behavior; parallel execution deferred to future enhancement
  - **Created:** 2025-10-06
