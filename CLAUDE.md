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

# Git Commits & Github Pull Request Format

## Guidelines
- Commit messages should be concise and descriptive
- Separate the subject from the body with a blank line
- Limit the subject to 50 characters
- Limit the body to 72 characters per line
- Do not end subject with a period
- Use the imperative mood in the subject line.
- If applicable, reference a GitHub issue in the body with `Resolves: #<issue-number>`

## Message Format
```
<type>[optional scope]: <description>
```

## Types
- Feat: A new feature
- Fix: A bug fix
- Chore: A chore (non-code change)
- Docs: Documentation changes
- Refactor: A code refactor
- Test: A test change
- Style: A code style change
- Perf: A performance improvement
- Build: A build change
- Ci: A continuous integration change
- Revert: A revert change

## Example Types with Optional Scope
- Feat(api): Add pagination to the users endpoint
- Fix(auth): Correct token expiration validation

## Example
```bash
git commit -m "$(cat <<'EOF'
Feat: Add user authentication endpoint

Implement the /api/login endpoint using JSON Web Tokens (JWT).
This is the first step towards securing the application by
requiring users to log in to access protected routes.

Resolves: #123
EOF
)"
```

# Important Directories

- `tests/` - All test files (Test suites should have their own subdirectory)
- `.claude/reports/` - Reports from AI agents