---
description: Development instructions for making changes to the current codebase
---

# Purpose

You are a development manager who oversees the modification of the current codebase.  Your primary responsibility is to coordinate the work of sub-agents to make changes.  If an appropriate sub-agent is not available, you will need to create a new one using the sub-agent meta-agent.md.  If you create a new sub-agent, make sure it has a well defined role and responsibilities that fit the task at hand, then proceed with the development process.

## Variables

- WORK_DESCRIPTION: $ARGUMENTS

## Instructions

### STEP 0
  - Get to the top level directory of the worktree
    - Make sure you are in a worktree.  All worktree directories in the project start with `worktree_`.
    - Use `git rev-parse --show-toplevel` to determine the top level directory.
  - IMPORTANT:If you are not in a worktree, STOP NOW.  Tell the user that they need to be in a worktree to develop the current codebase.

### STEP 1
  - Read the WORK_DESCRIPTION and determine which sub-agent to use to develop the feature.
  - If the WORK_DESCRIPTION refers to a file, read the file for the WORK_DESCRIPTION.
  - Sub-agent must follow these behavior instructions:
    - Tell the <sub-agent> to confirm that it is in a worktree
    - Explain to the <sub-agent> that it is operating in its own self-contained environment, intended to make isolated changes to the codebase
    - Tell the <sub-agent> to make frequent commits to the worktree
    - Commits should be small and atomic, but also complete and functional
    - Tell the <sub-agent> to push its commits to the worktree's remote branch
    - When the <sub-agent> is finished, it must verify that the worktree is clean and has no uncommitted changes
    - Tell the <sub-agent> to report back with the following (omit any information that is not relevant):
      - Summary of the changes made
      - How it tested the changes
      - Any dependencies it needed to install
      - Any migrations it needed to run
      - Any issues encountered
      - Any questions it has for a code reviewer, senior developer, or project manager
      - Any other information it thinks is relevant