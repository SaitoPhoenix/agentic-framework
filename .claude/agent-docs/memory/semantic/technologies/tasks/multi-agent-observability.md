---
name: multi-agent-observability
aliases:
  - multi_agent_observability
  - observability event sender
entity_classification: technology/task
status: new
created: 2025-10-13T17:50:00Z
last_updated: 2025-10-13T17:50:00Z
source_episodes:
  - 251013_EP_1
summary: A Claude Code hook task that sends observability events to an external server for monitoring multiple agents across projects, with optional LLM-powered summarization
ambiguities: []
relationships:
  - type: is_part_of
    entity: claude-code-hooks
    description: Multi-agent observability is a task component within the hooks system
    role: component
    source: 251013_EP_1
  - type: designed_by
    entity: yuki
    description: Yuki implemented the complete multi-agent observability task
    role: creation
    source: 251013_EP_1
  - type: uses
    entity: anthropic
    description: Uses Anthropic Claude models for LLM-based event summarization
    role: dependency
    source: 251013_EP_1
  - type: complements
    entity: tts-notification
    description: Follows similar LLM configuration pattern established by TTS notification
    role: peer task
    source: 251013_EP_1
---

## Facts

### Architecture
- Sends events via HTTP POST to configurable server endpoint [251013_EP_1]
- Supports all Claude Code hook types with event-specific handling [251013_EP_1]
- Uses LLM tools rather than subprocess calls for summarization [251013_EP_1]
- Reads chat transcripts from .jsonl files when needed [251013_EP_1]
- Follows fail-open design pattern to never block operations [251013_EP_1]

### Event Processing
- Pre/post tool use, notification, user prompt submit hooks trigger LLM summarization [251013_EP_1]
- Stop event includes full chat transcript [251013_EP_1]
- All other events send default information without special processing [251013_EP_1]
- Hook event type extracted from hook_event_name field in input_data [251013_EP_1]

### Configuration Options
- source_app: Application identifier (default: "claude-code") [251013_EP_1]
- server_host: Server hostname/IP (default: "localhost") [251013_EP_1]
- server_port: Server port number (default: 4000) [251013_EP_1]
- add_chat: Include chat transcript (optional, default: false) [251013_EP_1]
- summarize: Generate LLM summary (optional, default: false) [251013_EP_1]
- message_pattern: Jinja template for summarization prompt (required when summarize is true) [251013_EP_1]
- llm: LLM provider configuration object (required when summarize is true) [251013_EP_1]

### Payload Structure
- source_app: Identifies the originating application/agent [251013_EP_1]
- session_id: Unique session identifier [251013_EP_1]
- hook_event_type: Type of hook that triggered the event [251013_EP_1]
- payload: Original hook payload data [251013_EP_1]
- timestamp: Unix timestamp of event [251013_EP_1]
- chat: Optional conversation transcript array [251013_EP_1]
- summary: Optional LLM-generated event summary [251013_EP_1]

## Decisions

- **Use Jinja templates for summarization prompts** [251013_EP_1]
  - **Category:** Architecture
  - **Status:** Final
  - **Created:** 2025-10-13
  - **Rationale:** Allows flexible, reusable prompt templates stored in patterns directory
  - **Impact:** Created event_summary.j2 template in .claude/hooks/utils/patterns/

- **Configuration in hooks_config.yaml only** [251013_EP_1]
  - **Category:** Configuration Management
  - **Status:** Final
  - **Created:** 2025-10-13
  - **Rationale:** Keeps all configuration centralized, avoids unnecessary separate config files
  - **Impact:** No separate multi-agent-observability.yaml file created

- **Optional parameters with sensible defaults** [251013_EP_1]
  - **Category:** API Design
  - **Status:** Final
  - **Created:** 2025-10-13
  - **Rationale:** Minimizes required configuration while allowing customization
  - **Impact:** add_chat and summarize default to false, reducing config verbosity

## Accomplishments

### Implementation Complete
- Created main.py task implementation with full functionality [251013_EP_1]
- Converted summarize.txt to Jinja2 template (event_summary.j2) [251013_EP_1]
- Configured task on all hook types in hooks_config.yaml [251013_EP_1]
- Added comprehensive documentation to hooks config README [251013_EP_1]
- Successfully tested event sending to localhost:4000 [251013_EP_1]
- Fixed hook_event_name field extraction based on Anthropic documentation [251013_EP_1]

## Approaches

### Error Handling
- Fails silently by default unless verbose_logging enabled [251013_EP_1]
- Never raises exceptions that could block hook execution [251013_EP_1]
- System messages convey errors based on configuration flags [251013_EP_1]

### Configuration Design
- Minimal configuration with false defaults can be omitted [251013_EP_1]
- Message pattern required only when summarization enabled [251013_EP_1]
- Server configuration flexible with host and port separation [251013_EP_1]

### Development Process
- Research existing patterns first (TTS notification) [251013_EP_1]
- Implement in phases with validation between steps [251013_EP_1]
- Test with actual server before finalizing [251013_EP_1]
- Clean up configuration to keep it minimal [251013_EP_1]