---
name: git
aliases:
  - Git
entity_classification: technology/tool
status: active
created: 2025-10-13T17:50:00Z
last_updated: 2025-10-13T17:50:00Z
source_episodes:
  - 251013_EP_1
summary: Distributed version control system used for code management and collaboration
ambiguities: []
relationships:
  - type: used_by
    entity: yuki
    description: Yuki uses git for staging and committing code changes
    role: version control
    source: 251013_EP_1
---

## Facts

### Usage in Project
- Used for staging changes with `git add` command [251013_EP_1]
- Used for creating commits with descriptive messages [251013_EP_1]
- Commit messages follow specific format guidelines from CLAUDE.md [251013_EP_1]
- Current branch is main [251013_EP_1]

### Commit Message Format
- Type prefix followed by colon and description [251013_EP_1]
- Types include: Feat, Fix, Chore, Docs, Refactor, Test, Style, Perf, Build, Ci, Revert [251013_EP_1]
- Subject limited to 50 characters [251013_EP_1]
- Body limited to 72 characters per line [251013_EP_1]
- Imperative mood in subject line [251013_EP_1]

## Accomplishments

### Recent Commits
- Commit eba3cef: "Feat: Add multi-agent observability hook task" - 519 insertions across 4 files [251013_EP_1]