# Python Package Management with uv

Use uv exclusively for Python package management in this project.

## Package Management Commands

- All Python dependencies **must be installed, synchronized, and locked** using uv
- Never use pip, pip-tools, poetry, or conda directly for dependency management

Use these commands:

- Install dependencies: `uv add <package>`
- Remove dependencies: `uv remove <package>`
- Sync dependencies: `uv sync`

## Running Python Code

- Run a Python script with `uv run <script-name>.py`
- Run Python tools like Pytest with `uv run pytest` or `uv run ruff`
- Launch a Python repl with `uv run python`

## Managing Scripts with PEP 723 Inline Metadata

- Run a Python script with inline metadata (dependencies defined at the top of the file) with: `uv run script.py`
- You can add or remove dependencies manually from the `dependencies =` section at the top of the script, or
- Or using uv CLI:
    - `uv add package-name --script script.py`
    - `uv remove package-name --script script.py`

# Creating new features

When asked to create a new feature using a sub-agent, follow these steps:

1. Create a new worktree using the create_worktree sub-agent, use <feature-name> as the argument
2. After the worktree has been created, start feature development with the appropriate <sub-agent>.
3. In addition to work instructions, provide these behavior instructions to the feature development <sub-agent>
    - Tell the <sub-agent> to change its cwd to the worktree and create the feature there
    - Explain to the <sub-agent> that it is operating in its own self-contained environment, intended to build and test a single feature
    - Tell the <sub-agent> to make frequent commits to the worktree
    - Commits should be small and atomic, but also complete and functional
    - Tell the <sub-agent> to push its commits to the worktree's remote branch
    - When the <sub-agent> is finished, it must verify that the worktree is clean and has no uncommitted changes
    - Explain that a separate process will review the worktree and merge the changes into the main branch