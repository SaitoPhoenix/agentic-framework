---
name: claude-code-hooks
aliases:
  - hooks system
  - Claude Code hooks
  - hook system
entity_classification: technology/system
status: active
created: 2025-10-04T21:14:00Z
last_updated: 2025-10-06T00:00:00Z
source_episodes:
  - 251003_EP_7
  - 251006_EP_2
summary: A modular task-based system for extending Claude Code functionality through configurable hooks that execute at specific lifecycle events
ambiguities: []
relationships:
  - type: contains
    entity: security-guard
    description: Security guard is a task component within the hooks system
    role: parent system
    source: 251003_EP_7
  - type: contains
    entity: tts-notification
    description: TTS notification is a task component for audio feedback
    role: parent system
    source: 251003_EP_7
  - type: contains
    entity: hook-test-framework
    description: Hook test framework validates hooks system behavior
    role: parent system
    source: 251006_EP_2
  - type: uses
    entity: pathspec
    description: Uses pathspec library for pattern matching in security tasks
    role: consumer
    source: 251003_EP_7
---

## Facts

### Architecture
- Tasks are modular and reusable across different hooks [251003_EP_7]
- All tasks run sequentially within a hook [251003_EP_7]
- Task failures don't stop other tasks from running [251003_EP_7]
- Configuration is centralized in hooks_config.yaml [251003_EP_7]
- Tasks are located under .claude/hooks/tasks/ directory [251003_EP_7]

### Available Hooks
- session_start: Fires when a session begins [251003_EP_7]
- user_prompt_submit: Fires when user submits a prompt [251003_EP_7]
- pre_tool_use: Fires before a tool is executed [251003_EP_7]
- post_tool_use: Fires after a tool completes [251003_EP_7]
- stop: Fires when conversation ends [251003_EP_7]

### Task Components
- log_hook: Logs hook input data to JSON files [251003_EP_7]
- tts_notification: Provides text-to-speech notifications [251003_EP_7]
- conversation_capture: Captures conversation transcripts [251003_EP_7]
- cleanup_subprocesses: Terminates running subprocesses [251003_EP_7]
- security_guard: Validates and blocks dangerous operations [251003_EP_7]

### Configuration System
- Each task has module, function, and config properties [251003_EP_7]
- Tasks can be enabled/disabled via enabled flag [251003_EP_7]
- Configuration supports both required and optional parameters [251003_EP_7]
- Documentation maintained in .claude/hooks/config/README.md [251003_EP_7]

### Testing Infrastructure
- Comprehensive test framework located in .claude/hooks/test/ [251006_EP_2]
- Test payloads organized by hook type in structured directories [251006_EP_2]
- Automated test discovery and execution [251006_EP_2]
- Multiple validation strategies (json, exitcode, text) [251006_EP_2]
- JSON and Markdown report generation [251006_EP_2]
- 57 security guard tests with 100% pass rate [251006_EP_2]

## Requirements

- **Environment variables for API providers** [251003_EP_7]
  - **Category:** Configuration
  - **Priority:** Critical
  - **Status:** Active
  - **Details:** API keys must be set for TTS and LLM providers being used
  - **Created:** 2025-10-03

## Decisions

- **Modular task architecture over monolithic scripts** [251003_EP_7]
  - **Category:** Architecture
  - **Status:** Final
  - **Created:** 2025-10-03
  - **Rationale:** Enables reusability, maintainability, and cleaner separation of concerns
  - **Impact:** All hook functionality implemented as separate tasks

- **File-based configuration over inline configuration** [251003_EP_7]
  - **Category:** Configuration Management
  - **Status:** Final
  - **Created:** 2025-10-03
  - **Rationale:** Keeps configuration files clean and manageable
  - **Impact:** Complex configurations stored in separate YAML files

## Accomplishments

### Testing Infrastructure
- Built comprehensive test framework for all hook types [251006_EP_2]
- Created 57 test payloads covering security guard functionality [251006_EP_2]
- Implemented automated test migration tools [251006_EP_2]
- Achieved 100% test pass rate for security guard [251006_EP_2]

## Approaches

### Error Handling
- Verbose errors print to stdout when enabled [251003_EP_7]
- Silent failures by default unless verbose_errors is true [251003_EP_7]
- Validation can run separately from execution [251003_EP_7]

### Documentation Strategy
- Centralized documentation in config/README.md [251003_EP_7]
- Task documentation includes purpose, use cases, and configuration [251003_EP_7]
- Examples provided for common scenarios [251003_EP_7]
- Troubleshooting section for common issues [251003_EP_7]

### Testing Strategy
- Comprehensive test coverage with multiple categories [251006_EP_2]
- Automated test discovery and execution [251006_EP_2]
- Multiple validation strategies for different output types [251006_EP_2]
- Both JSON and Markdown reporting for different audiences [251006_EP_2]
