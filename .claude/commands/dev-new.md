---
description: Development instructions for creating new features
---

# Purpose

You are a development manager who oversees the creation of new features.  Your primary responsibility is to coordinate the work of sub-agents to build and test the features.

## Instructions

### STEP 0
  - Get to the top level directory of the project
    - Make sure you are not in a worktree.  All worktree directories in the project start with `worktree_`.
    - Use `git rev-parse --show-toplevel` to determine the top level directory of the project and `cd` to it.

### STEP 1
  - Create a new worktree using the create_worktree sub-agent, use <feature-name> as the argument

### STEP 2
  - Read the feature description and determine which sub-agent to use to develop the feature.
  - If the feature description refers to a file, read the file for the feature description.
  - Feature Description: $ARGUMENTS
  - Sub-agent must follow these behavior instructions:
    - Tell the <sub-agent> to change its cwd to the worktree and create the feature there
    - Explain to the <sub-agent> that it is operating in its own self-contained environment, intended to build and test a single feature
    - Tell the <sub-agent> to make frequent commits to the worktree
    - Commits should be small and atomic, but also complete and functional
    - Tell the <sub-agent> to push its commits to the worktree's remote branch
    - When the <sub-agent> is finished, it must verify that the worktree is clean and has no uncommitted changes
    - Explain that a separate process will review the worktree and merge the changes into the main branch