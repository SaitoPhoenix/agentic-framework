---
name: event-summary-j2
aliases:
  - event_summary.j2
entity_classification: technology/template
status: new
created: 2025-10-13T17:50:00Z
last_updated: 2025-10-13T17:50:00Z
source_episodes:
  - 251013_EP_1
summary: Jinja2 template for generating LLM prompts to summarize observability events
ambiguities: []
relationships:
  - type: used_by
    entity: multi-agent-observability
    description: Template used to generate summarization prompts
    role: prompt template
    source: 251013_EP_1
---

## Facts

### Location and Purpose
- Stored in .claude/hooks/utils/patterns/ directory [251013_EP_1]
- Converted from original summerize.txt file [251013_EP_1]
- Uses Jinja2 variables: event_type and payload_str [251013_EP_1]

### Content Structure
- Prompts for concise, technical one-sentence summaries [251013_EP_1]
- Accepts event type and payload as template variables [251013_EP_1]
- Focuses on key information extraction from events [251013_EP_1]