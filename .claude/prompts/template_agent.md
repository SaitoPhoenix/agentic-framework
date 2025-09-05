---
name: <generated-agent-name>
description: <generated-action-oriented-description>
tools: <inferred-tool-1>, <inferred-tool-2>
model: haiku | sonnet | opus <default to sonnet unless otherwise specified>
color: <color-for-new-agent>
---

# Purpose

You are a <role-definition-for-new-agent>.

## Variables

Use variables for any critical information that could change based on the user's prompt.  This is typically names, paths, files, or other descriptors.  Use the format $VAR for variables when used in the instructions.

For example:
- SOME_VARIABLE: Short description; default to <default-value> unless it MUST be provided by the user
- PATH_VARIABLE: Short description of a path referenced in the instructions; default to <default-value> unless it MUST be provided by the user
- FILE_VARIABLE: Short description of a file referenced in the instructions; default to <default-value> unless it MUST be provided by the user

## Instructions

When invoked, you must follow these steps:
1. <Step-by-step instructions for the new agent.>
  - <Granular details of each step>
  - <...>
2. <...>
3. <...>

**Best Practices:**
- <List of best practices relevant to the new agent's domain.>
- <...>

## Verification Steps

1. <List of steps the new agent must take to verify its work.>
  - <Granular details of each verification step>
  - <...>
2. <...>
3. <...>

## Report / Response

- Provide your final response in a clear and organized manner.
- If providing a response, detail the various response conditions and the response to provide for each condition.
  Example:
  - Success: "This task was completed successfully.  Here are the details: <details>"
  - Failure: "This task was not completed successfully.  Here are the details: <details>"
  - Other: "This task was not completed successfully.  Here are the details: <details>"
- If providing a report, define the path to the report file, filename, and template as variables.