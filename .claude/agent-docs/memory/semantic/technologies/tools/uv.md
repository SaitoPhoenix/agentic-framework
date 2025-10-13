---
name: uv
aliases:
  - UV
entity_classification: technology/tool
status: active
created: 2025-10-13T17:50:00Z
last_updated: 2025-10-13T17:50:00Z
source_episodes:
  - 251013_EP_1
summary: Modern Python package and project management tool used exclusively for dependency management and script execution
ambiguities: []
relationships:
  - type: preferred_by
    entity: saito
    description: Saito insists on using uv for all Python execution
    role: tool choice
    source: 251013_EP_1
---

## Facts

### Usage
- Used exclusively for Python package management in the project [251013_EP_1]
- Required for running Python scripts with `uv run` command [251013_EP_1]
- Manages dependencies with `uv add` and `uv remove` commands [251013_EP_1]
- Synchronizes dependencies with `uv sync` command [251013_EP_1]

### Configuration
- Mentioned in project CLAUDE.md as the exclusive Python package manager [251013_EP_1]
- Never use pip, pip-tools, poetry, or conda directly [251013_EP_1]