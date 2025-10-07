---
description: Sets up and runs the memory creation process
argument-hint: [episodic memory file]
---

# Create Memories

## Variables

- **EPISODIC_MEMORY**: $ARGUMENTS
- **AGENTS_PATH**: .claude/agents/
- **TIMESTAMP**: Current timestamp

## Files

- **SEMANTIC_SYNTHESIST**: $AGENTS_PATH/semantic-synthesist.md
- **REVIEWER**: $AGENTS_PATH/semantic-synthesist-reviewer.md

## Workflow
1. *Run:* `date -Im` to get $TIMESTAMP
2. Task the $SEMANTIC_SYNTHESIST agent to create a new semantic memories from $EPISODIC_MEMORY, and give them $TIMESTAMP
3. Once the semantic memories are created, Task the $REVIEWER agent to review the semantic memories and include these details:
   - Provide them the $TIMESTAMP
   - Tell them the $EPISODIC_MEMORY that the synthesis is based on
   - Remind them to only check if $EPISODIC_MEMORY exists, do not read the file
4. *Response:* Provide the exact final response from the $REVIEWER agent.