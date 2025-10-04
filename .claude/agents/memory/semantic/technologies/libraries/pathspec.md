---
name: pathspec
aliases:
  - pathspec library
entity_classification: technology/library
status: active
created: 2025-10-04T21:14:00Z
last_updated: 2025-10-04T21:14:00Z
source_episodes:
  - 251003_EP_7
summary: A Python library that provides gitignore-style pattern matching for file paths
ambiguities: []
relationships:
  - type: used_by
    entity: security-guard
    description: Security guard task uses pathspec for file pattern matching
    role: dependency
    source: 251003_EP_7
  - type: used_by
    entity: claude-code-hooks
    description: Added as a dependency to hook_entry.py for pattern matching
    role: dependency
    source: 251003_EP_7
---

## Facts

### Usage
- Added to hook_entry.py inline metadata dependencies [251003_EP_7]
- Provides gitignore-style pattern matching functionality [251003_EP_7]
- Used for matching file patterns like **/test.md [251003_EP_7]
- Handles negation patterns with ! prefix [251003_EP_7]

## Suggestions

### Implementation Choice
- Recommended over implementing custom pattern matching [251003_EP_7]
- Standard, well-tested library for gitignore patterns [251003_EP_7]