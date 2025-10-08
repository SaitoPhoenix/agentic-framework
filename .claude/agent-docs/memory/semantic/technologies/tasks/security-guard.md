---
name: security-guard
aliases:
  - security_guard task
  - hooks security guard
entity_classification: technology/task
status: active
created: 2025-10-04T21:14:00Z
last_updated: 2025-10-06T00:00:00Z
source_episodes:
  - 251003_EP_7
  - 251006_EP_2
summary: A modular task for Claude Code hooks that provides configurable security controls to prevent accidental exposure of sensitive files and execution of dangerous commands
ambiguities: []
relationships:
  - type: is_part_of
    entity: claude-code-hooks
    description: Security guard is a reusable task component in the hooks system
    role: security component
    source: 251003_EP_7
  - type: uses
    entity: pathspec
    description: Uses pathspec library for gitignore-style file pattern matching
    role: consumer
    source: 251003_EP_7
  - type: designed_by
    entity: yuki
    description: Yuki implemented the security guard task based on Saito's requirements
    role: implementation
    source: 251003_EP_7
  - type: used_by
    entity: hook-test-framework
    description: Security guard is tested by the comprehensive hook test framework
    role: test subject
    source: 251006_EP_2
---

## Facts

### Architecture
- Replaces monolithic pre_tool_use.py with modular task-based approach [251003_EP_7]
- Consists of multiple Python modules: main.py, file_matcher.py, command_matcher.py, validator.py, rule_loader.py [251003_EP_7]
- Uses YAML configuration file (security-rules.yaml) for rule definitions [251003_EP_7]
- Supports both file-based and command-based security rules [251003_EP_7]
- Tasks run sequentially and continue even if one fails [251003_EP_7]

### Configuration Structure
- Rules are organized into whitelist and blacklist sections [251003_EP_7]
- Each section has three permission levels: allow, ask, deny [251003_EP_7]
- Whitelist rules take precedence over blacklist rules [251003_EP_7]
- Most restrictive permission wins within each list (deny > ask > allow) [251003_EP_7]
- Default permission is deny if not specified [251003_EP_7]

### Features
- Gitignore-style file pattern matching using pathspec library [251003_EP_7]
- Command matching with flags, paths, and regex patterns [251003_EP_7]
- Tool-specific rules via optional tools attribute [251003_EP_7]
- Custom messages with sensible defaults [251003_EP_7]
- Validation mode for checking rules on session start [251003_EP_7]
- All matches are logged regardless of permission level [251003_EP_7]

### Pattern Matching Behavior
- File patterns use gitignore syntax (e.g., **/test.md matches test.md anywhere) [251003_EP_7]
- Command paths are matched as literal arguments only [251003_EP_7]
- Regex patterns can be specified explicitly for advanced matching [251003_EP_7]
- When multiple conditions exist (flags AND paths), ALL must match [251003_EP_7]

### Test Coverage
- Comprehensive test suite with 57 test cases [251006_EP_2]
- Whitelist tests: 4 (validate allowed patterns like .env.example) [251006_EP_2]
- Deny tests: 20 (validate blocked operations like .env files and rm -rf commands) [251006_EP_2]
- Ask tests: 10 (validate confirmation prompts for chmod, curl|bash, git push -f) [251006_EP_2]
- Edge case tests: 12 (uppercase filenames, spaces, path traversal, environment variables) [251006_EP_2]
- Future enhancement tests: 11 (document potential rules not yet implemented) [251006_EP_2]
- 100% test pass rate achieved after migration to new test framework [251006_EP_2]

## Decisions

- **Use file-based rules only, no inline configuration** [251003_EP_7]
  - **Category:** Architecture
  - **Status:** Final
  - **Created:** 2025-10-03
  - **Rationale:** Simplifies configuration management and keeps hooks_config.yaml clean
  - **Impact:** All security rules must be defined in security-rules.yaml

- **Group rules by permission level in hierarchy** [251003_EP_7]
  - **Category:** Configuration Design
  - **Status:** Final
  - **Created:** 2025-10-03
  - **Rationale:** Makes it clearer which rules have which permission level
  - **Impact:** Rules are organized as whitelist/blacklist -> permission level -> rules

- **Remove negation operator (!) from patterns** [251003_EP_7]
  - **Category:** Configuration Syntax
  - **Status:** Final
  - **Created:** 2025-10-03
  - **Rationale:** The ! prefix was unnecessary since whitelist/blacklist behavior is determined by section placement
  - **Impact:** Cleaner, less confusing pattern syntax

## Requirements

- **API keys must be set for TTS notification providers** [251003_EP_7]
  - **Category:** Environment Configuration
  - **Priority:** Critical
  - **Status:** Active
  - **Details:** OPENAI_API_KEY, ANTHROPIC_API_KEY, GCLOUDTTS_SERVICE_KEY, ELEVENLABS_API_KEY, TABBY_API_KEY, or OLLAMA_API_KEY depending on provider
  - **Created:** 2025-10-03

## Accomplishments

### Implementation
- Created complete security_guard task structure with 5 Python modules [251003_EP_7]
- Implemented gitignore-style file pattern matching [251003_EP_7]
- Implemented command matching with AND logic for multiple conditions [251003_EP_7]
- Added pathspec dependency to hook_entry.py [251003_EP_7]
- Created comprehensive security-rules.yaml template [251003_EP_7]
- Updated hooks_config.yaml with security_guard configurations [251003_EP_7]
- Documented security_guard in hooks configuration README [251003_EP_7]

### Testing
- Validated security rules on session_start [251003_EP_7]
- Tested file blocking (.env blocked, .env.example allowed) [251003_EP_7]
- Tested command blocking (rm -rf /, sudo, chmod 777) [251003_EP_7]
- Verified whitelist precedence over blacklist [251003_EP_7]
- Confirmed permission levels work correctly (deny, ask, allow) [251003_EP_7]
- Fixed command matching logic to use AND for multiple conditions [251003_EP_7]
- Fixed path matching to only match literal arguments [251003_EP_7]
- Created 57 comprehensive test payloads covering all security rules [251006_EP_2]
- Tested all payloads with 100% pass rate [251006_EP_2]
- Created edge case tests for boundary conditions [251006_EP_2]
- Created future enhancement tests documenting potential security rules [251006_EP_2]
- Migrated all tests to new test framework format [251006_EP_2]

## Approaches

### Error Handling
- Verbose errors print to stdout when enabled for command-line testing [251003_EP_7]
- Tasks fail silently by default with no indication unless verbose_errors is true [251003_EP_7]
- Validation errors are reported to stderr during session_start [251003_EP_7]

### Testing Strategy
- Test individual components through hook_entry.py with JSON input [251003_EP_7]
- Use echo command piped to hook_entry.py for testing specific scenarios [251003_EP_7]
- Iterative testing and fixing based on observed behavior [251003_EP_7]
- Comprehensive test suite organized by category and priority [251006_EP_2]
- Automated test migration with validation rules [251006_EP_2]
- Edge case testing for unusual inputs and boundary conditions [251006_EP_2]

## Suggestions

### Security Enhancements
- Add patterns for .git-credentials files [251006_EP_2]
- Add patterns for .npmrc files with auth tokens [251006_EP_2]
- Add patterns for .netrc files [251006_EP_2]
- Add patterns for .pgpass PostgreSQL password files [251006_EP_2]
- Add patterns for Docker credential files (~/.docker/config.json) [251006_EP_2]
- Add patterns for Kubernetes config with credentials (~/.kube/config) [251006_EP_2]
- Add patterns for private GPG keys (*.gpg, *.asc) [251006_EP_2]
- Add rules for dd command (can wipe disks) [251006_EP_2]
- Add rules for mkfs.* commands (filesystem formatting) [251006_EP_2]
- Add rules for modification of system files (/etc/passwd, /etc/shadow) [251006_EP_2]
