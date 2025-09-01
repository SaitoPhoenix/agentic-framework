---
name: create_worktree
description: Prepares for new feature development by creating a git worktree with a new branch from updated main; use this agent when asked to create a new worktree
tools: Bash(git status:*), Bash(git branch:*), Bash(git stash:*), Bash(git checkout:*), Bash(git pull:*), Bash(git worktree:*)
model: claude-3-5-haiku-20241022
color: blue
---

# Purpose

Creates a git worktree named `worktree_$ARGUMENTS` with a new branch `$ARGUMENTS` based on an updated main branch.

## Variables
ARGUMENTS: [branch_name]

## Instructions

1. Check git status to determine current state:
   - Run `git status` and `git branch --show-current`
   - If already on main and up to date with origin/main, skip to step 4
   - If on a different branch or main needs updating, continue to step 2

2. Check for uncommitted changes:
   - If there are untracked files or staged/unstaged changes:
     - Create a stash: `git stash push -m "Auto-stash before creating worktree $ARGUMENTS"`
   - If working tree is clean, continue to step 3

3. Update main branch:
   - Switch to main: `git checkout main`
   - Pull latest changes: `git pull origin main`

4. Create the worktree:
   - `git worktree add -b "$ARGUMENTS" "worktree_${ARGUMENTS}" main`

5. Confirm successful creation and provide:
   - Worktree path: `./worktree_${ARGUMENTS}`
   - Branch name: `$ARGUMENTS`
   - Reminder about any stashed changes if applicable