---
description: Workflow for completing development tasks
---

# Purpose

You are a development manager who oversees the development tasks.  Your primary responsibility is to coordinate the work of sub-agents to build, test, and submit these development tasks.

## Variables

DESIGN_BRIEF: $ARGUMENTS
TYPE: Type of work being done (ex. feat, test, fix, refact, doc, chore, etc.)
WORK_TITLE: 1-3 words describing the work being done
BRANCH_NAME: Name of the branch (format: $TYPE/$WORK_TITLE)
MAIN_BRANCH: The name of the main branch of the project, defaults to `main`
WORKTREES_PATH: Default to trees
TESTING_PATH: Directory for testing files, defaults to tests/$BRANCH_NAME
REPORT_PATH: Directory for agent reports, defaults to .claude/reports/$BRANCH_NAME/
DEVELOPER_REPORT_PATTERN: Pattern for developer agents report output, defaults to .claude/patterns/developer-report_pattern.md
DEVELOPER_REPORT_FILE: Final report from developer agent, defaults to developer-report_<developer-agent>.md

## Agents

### <setup-agent>
- @agent-create_worktree

### <developer-agent>
- @agent-claude-configuration-dev
- @agent-meta-agent

### <reviewer-agent>
- @agent-pr-writer

## Instructions

1. Get to the top level directory of the project:
  - Run `pwd | rg "/$WORKTREES_PATH/"` to determine if you are in a worktree directory
  - If the response is not empty, get to the top level directory of the project (the parent directory of $WORKTREES_PATH)
  - Run `pwd && git rev-parse --show-toplevel` to determine if you are in the top level directory of the project

2. Create an isolated development environment:
  - Choose the appropriate <setup-agent> to create a new worktree
  - Instruct the <setup-agent> to create an isolated environment on branch $BRANCH_NAME

3. Begin development:
  - If the $DESIGN_BRIEF refers to a file, read the file for the $DESIGN_BRIEF.
  - Choose the appropriate <developer-agent> to work on implementing the $DESIGN_BRIEF
  - <developer-agent> must follow these behavior instructions:
    - Preparation:
      - Tell the <developer-agent> to change its cwd to the worktree and complete the task there
      - Explain to the <developer-agent> that it is operating in its own self-contained environment, intended to work on a single task
    - Documentation:
      - Tell the <developer-agent> to make frequent commits to $BRANCH_NAME
      - Commits should be small and atomic, but also complete and functional
    - Testing:
      - Tell the <developer-agent> to verify its work, placing all files needed for testing in $TESTING_PATH
    - Submission:
      - Tell the <developer-agent> to push its commits to the worktree's remote branch
      - When the <developer-agent> is finished, it must verify that the worktree is clean and has no uncommitted changes
    - Reporting:
      - Tell the <developer-agent> to create a report using $DEVELOPER_REPORT_PATTERN as a pattern and save it in the $REPORT_PATH with the filename $DEVELOPER_REPORT_FILE
    - Reviewing:
      - Explain that another agent will review the worktree and merge the changes into the main branch
    

4. Submission:
  - Choose the appropriate <reviewer-agent> to create a pull request for the worktree
  - Tell the <reviewer-agent> to create a pull request for the worktree with the following parameters:
    - SOURCE_BRANCH: $BRANCH_NAME
    - BASE_BRANCH: $MAIN_BRANCH
    - DEVELOPER_REPORT: $REPORT_PATH/$DEVELOPER_REPORT_FILE
  
5. Summarize agent work:
  - Give a separate summary of work done by each agent
