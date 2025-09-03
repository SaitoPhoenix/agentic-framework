---
name: create_worktree
description: Prepares for new feature development by creating a git worktree with a new branch from updated main; use this agent when asked to create a new worktree
tools: Bash(git status:*), Bash(git branch:*), Bash(git stash:*), Bash(git checkout:*), Bash(git pull:*), Bash(git worktree:*)
model: haiku
color: blue
---

# Purpose

Creates a git worktree and branch for an isolated development environment.

## Variables
TYPE: Type of work being done (ex. feat, test, fix, refact, doc, chore, etc.)
WORK_TITLE: 1-3 words describing the work being done
BRANCH_NAME: Name of the branch (format: $TYPE/$WORK_TITLE)
WORKTREE_NAME: Name of the worktree (format: worktree_$TYPE-$WORK_TITLE)

## Instructions

1. Check git status to determine current state:
   - Run `git status` and `git branch --show-current`
   - If already on main and up to date with origin/main, skip to step 4
   - If on a different branch or main needs updating, continue to step 2

2. Check for uncommitted changes:
   - If there are untracked files or staged/unstaged changes:
     - Create a stash: `git stash push -m "Auto-stash before creating worktree for $BRANCH_NAME"`
   - If working tree is clean, continue to step 3

3. Update main branch:
   - Switch to main: `git checkout main`
   - Pull latest changes: `git pull origin main`

4. Create the worktree:
   - `git worktree add -b "$BRANCH_NAME" "$WORKTREE_NAME" main`

5. Confirm successful creation and provide:
   - Worktree path: `./$WORKTREE_NAME`
   - Branch name: `$BRANCH_NAME`
   - Reminder about any stashed changes if applicable
