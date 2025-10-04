---
name: tts-notification
aliases:
  - TTS notification task
  - text-to-speech notification
entity_classification: technology/task
status: active
created: 2025-10-04T21:14:00Z
last_updated: 2025-10-04T21:14:00Z
source_episodes:
  - 251003_EP_7
summary: A Claude Code hooks task that provides text-to-speech notifications with optional LLM-generated messages
ambiguities: []
relationships:
  - type: is_part_of
    entity: claude-code-hooks
    description: TTS notification is a reusable task component in the hooks system
    role: notification component
    source: 251003_EP_7
---

## Facts

### Configuration
- LLM configuration is optional - if not provided, renders pattern directly to TTS [251003_EP_7]
- Supports multiple TTS providers: gcloud, openai, elevenlabs, pyttsx3 [251003_EP_7]
- Supports multiple LLM providers: openai, anthropic, tabby, ollama [251003_EP_7]
- Can randomly select messages when choose_random is true [251003_EP_7]
- Message patterns located in .claude/hooks/utils/patterns/ [251003_EP_7]

### Pattern Processing
- Uses Jinja2 templates for message patterns [251003_EP_7]
- If choose_random is true, renders template twice: first for random selection, second for placeholders [251003_EP_7]
- Pattern files can contain sets of messages for random selection [251003_EP_7]

### Provider Examples
- OpenAI voices: alloy, echo, fable, onyx, nova, shimmer [251003_EP_7]
- Google Cloud voices: en-US-Chirp3-HD-Despina, en-US-Wavenet-F [251003_EP_7]

## Decisions

- **Make LLM configuration optional** [251003_EP_7]
  - **Category:** Feature Design
  - **Status:** Final
  - **Created:** 2025-10-03
  - **Rationale:** Not all use cases require LLM generation - sometimes direct TTS is sufficient
  - **Impact:** Simplified configuration for basic TTS use cases