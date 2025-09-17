---
allowed-tools: Bash, Read
description: Load context for a new agent session by analyzing codebase structure, documentation and README
---

# Prime

Run commands and read files to get a high level understanding of the project.

## Workflow
1. *Run:* `eza --tree --only-dirs --all --ignore-glob=".git|__*|node_modules|dist|build|.vscode|.idea|.venv|target|coverage|.cursor"`
2. *Run:* `git status`
3. *Run:* `git diff HEAD origin/main`
4. *Run:* `git branch --show-current`
5. *Read:* Review the files listed under `Read` to understand the project's purpose and functionality
6. *Report:* Provide a summary of your understanding of the project

### Read
- README.md

## Report

- Provide a summary of your understanding of the project
- Include key directories, describing their purpose
- Inform the user of the current state of the git repository