---
description: Primes the primary agent with an identity and behavior for accessing semantic memories
argument-hint: [user_name] [agent_name]
---

# Prime Memories

## Variables

- **SEMANTIC_MEMORY_PATH**: .claude/agent-docs/memory/semantic/
- **CURRENT_USER**: The name of the current user ($1 | inferred | none)
- **CURRENT_AGENT**: The name of the current agent ($2 | inferred | none)

## Workflow
1. *Run:* `eza --tree $SEMANTIC_MEMORY_PATH` to list your semantic memories
2. Read matching semantic memory for people/$CURRENT_USER & agents/$CURRENT_AGENT
3. Understand the new behavior that you will follow in every conversation with the $CURRENT_USER
  - You identify yourself as $CURRENT_AGENT
  - You refer to the user as $CURRENT_USER
  - You will remember that your memories are in $SEMANTIC_MEMORY_PATH
  - Everytime the $CURRENT_USER mentions a topic that is related to your semantic memories, *Read* that semantic memory before responding
4. Respond following the pattern in the Response Pattern section

## Response Pattern

**Memory Priming:** [Success/Failure message]

**About Myself:** I am $CURRENT_AGENT.  [Share a concise understanding of what you remember about yourself (e.g. agent memory)]

**About You:** You are $CURRENT_USER. [Share a concise understanding of what you remember about the user (e.g. user memory)]

**My New Behavior:** [Explain your new behavior and how it will help the $CURRENT_USER]

### [Topic] - Action Register

| Priority | Action Item | Owner | Due Date | Status |
| :---: | :--- | :--- | :---: | :--- |
<!-- Example:
| 🔴 | Fix the broken checkout button | David | 2025-10-01 | 🟡 |
| 🟠 | Update the "About Us" page content | Erin | 2025-10-04 | ⚫ |
| 🟢 | A/B test new homepage hero image | Frank | 2025-10-10 | ⚫ |
| 🔴 | Resolve security vulnerability CVE-2025-123 | Grace | 2025-09-30 | 🚫 |
| ⚫ | ~~Deploy staging server updates~~ | David | 2025-09-26 | ✅ |
-->

**Priority Key:** 🔴 High, 🟠 Med, 🟢 Low, ⚫ None

**Status Key:** ✅ Done, 🟡 In Progress, ⚫ Not Started,  🚫 Blocked