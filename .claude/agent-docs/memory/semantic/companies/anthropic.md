---
name: anthropic
aliases:
  - Anthropic
entity_classification: company
status: new
created: 2025-10-13T17:50:00Z
last_updated: 2025-10-13T17:50:00Z
source_episodes:
  - 251013_EP_1
summary: AI company that provides Claude language models used for event summarization in the observability system
ambiguities: []
relationships:
  - type: used_by
    entity: multi-agent-observability
    description: Provides LLM API for generating event summaries
    role: service provider
    source: 251013_EP_1
  - type: used_by
    entity: tts-notification
    description: Provides LLM services for TTS notification task
    role: service provider
    source: 251013_EP_1
---

## Facts

### Services
- Provides Claude language models via API [251013_EP_1]
- claude-3-5-haiku-latest model used for event summarization [251013_EP_1]
- Supports function calling and structured outputs [251013_EP_1]

### Documentation
- Maintains anthropic_hooks.md reference documentation [251013_EP_1]
- Documents hook_event_name field structure for hooks [251013_EP_1]