---
description: Development instructions for creating new features
---

# Purpose

You are a development manager who oversees the creation of new features.  Your primary responsibility is to coordinate the work of sub-agents to build and test the features.

## Variables

- WORK_DESCRIPTION: $ARGUMENTS
- BRANCH_NAME: Determine the name of the branch based on the WORK_DESCRIPTION
- MAIN_BRANCH: The name of the main branch of the project, defaults to `main`

## Instructions

### STEP 0
  - Get to the top level directory of the project
    - Make sure you are not in a worktree.  All worktree directories in the project start with `worktree_`.
    - Use `git rev-parse --show-toplevel` to determine the top level directory of the project and `cd` to it.

### STEP 1
  - Create a new worktree using the create_worktree sub-agent, provide the BRANCH_NAME as the argument

### STEP 2
  - Read the WORK_DESCRIPTION and determine which sub-agent to use to develop the feature, they will be known as <feature-agent>
  - If the WORK_DESCRIPTION refers to a file, read the file for the WORK_DESCRIPTION.
  - <feature-agent> must follow these behavior instructions:
    - Tell the <feature-agent> to change its cwd to the worktree and create the feature there
    - Explain to the <feature-agent> that it is operating in its own self-contained environment, intended to build and test a single feature
    - Tell the <feature-agent> to make frequent commits to the worktree
    - Commits should be small and atomic, but also complete and functional
    - Tell the <feature-agent> to push its commits to the worktree's remote branch
    - When the <feature-agent> is finished, it must verify that the worktree is clean and has no uncommitted changes
    - Explain that a separate process will review the worktree and merge the changes into the main branch
    - Tell the <feature-agent> to report back using .claude/prompts/developer-report.md as a template

### STEP 3
  - Use the pr-writer sub-agent to create a pull request for the worktree
  - Provide the BRANCH_NAME as the SOURCE_BRANCH
  - Provide the MAIN_BRANCH as the BASE_BRANCH
  - Provide the report from the <feature-agent> as the DEVELOPER_REPORT

### STEP 4
  - Give a separate summary of work done by each sub-agent
