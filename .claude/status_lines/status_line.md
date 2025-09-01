# Claude Code Status Line Documentation

Status lines provide real-time context about your Claude Code session in the terminal. They appear at the bottom of your terminal and update dynamically as you work.

## Configuration

Status lines are configured in `.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "uv run .claude/status_lines/status_line_v4.py",
    "padding": 0
  }
}
```

To change the active status line, update the `command` field to point to a different script.

## Available Status Lines

### Version 1: Basic Model and Directory Status
**File:** `status_line.py`  
**Format:** `[Model] | 📁 Directory | 🌿 Branch ±changes | vVersion`

**Components:**
- **Model**: Current AI model name (cyan)
- **Directory**: Current working directory basename (blue)
- **Git Branch**: Current git branch with uncommitted change count (green)
- **Version**: Claude Code version (gray)

**Example:**
```
[Claude 3 Opus] | 📁 my-project | 🌿 main ±3 | v1.0.92
```

**Use Case:** Best for developers who want to see their git status and current directory at a glance.

---

### Version 2: Last User Prompt Display
**File:** `status_line_v2.py`  
**Format:** `[Model] 💬 Last user prompt text...`

**Components:**
- **Model**: Current AI model name (cyan)
- **Icon**: Context-aware emoji based on prompt type
  - ⚡ Command (starts with /)
  - ❓ Question (contains ?)
  - 💡 Creation (create, write, add, implement, build)
  - 🐛 Debug (fix, debug, error, issue)
  - ♻️ Refactor (refactor, improve, optimize)
  - 💬 General conversation
- **Prompt**: Last user prompt with context-aware coloring

**Example:**
```
[Claude 3 Opus] 💡 Create a Python web scraper for news articles
```

**Color Scheme:**
- Yellow: Commands
- Blue: Questions
- Green: Creation tasks
- Red: Debug/fix tasks
- Magenta: Refactor tasks
- White: General prompts

**Use Case:** Ideal for tracking what task Claude is currently working on.

---

### Version 3: Agent Name with Prompt History
**File:** `status_line_v3.py`  
**Format:** `[Agent] [Model] 💬 Current prompt | Previous prompt | Older prompt`

**Components:**
- **Agent**: Session agent name (bright red) - e.g., FLUX, PRISM, SYNTH
- **Model**: Current AI model name (blue)
- **Current Prompt**: Most recent prompt, 75 chars (bright white)
- **Previous Prompt**: Second most recent, 50 chars (gray)
- **Older Prompt**: Third most recent, 30 chars (dark gray)

**Example:**
```
[FLUX] [Claude 3 Opus] 💡 Create a web scraper... | Fix the bug in... | Add tests...
```

**Use Case:** Perfect for users who want to see their conversation history at a glance.

---

### Version 4: Agent Name with Current Prompt and Extras ⭐ **(Currently Active)**
**File:** `status_line_v4.py`  
**Format:** `[Agent] | [Model] | 💬 Current prompt... | [extras:values]`

**Components:**
- **Agent**: Session agent name (bright red) - dynamically generated names like FLUX, PRISM, SYNTH
- **Model**: Current AI model name (blue)
- **Current Prompt**: Most recent prompt, 100 chars (bright white)
- **Extras**: Optional session metadata (cyan) - custom key:value pairs

**Example:**
```
[SYNTH] | [Claude 3 Opus] | 💡 Create a REST API server... | [mode:dev env:local]
```

**Use Case:** The most comprehensive status line, showing agent identity, current task, and session metadata.

---

## Adding Custom Status Lines

To create a new status line:

1. **Create a new Python script** in `.claude/status_lines/`:
   ```python
   #!/usr/bin/env -S uv run --script
   # /// script
   # requires-python = ">=3.11"
   # dependencies = ["python-dotenv"]
   # ///
   
   """
   Status Line vX - Your Description
   
   FORMAT: Your format here
   EXAMPLE: Your example here
   """
   
   import json
   import sys
   
   def generate_status_line(input_data):
       # Your logic here
       return "Your formatted status line"
   
   def main():
       try:
           input_data = json.loads(sys.stdin.read())
           status_line = generate_status_line(input_data)
           print(status_line)
           sys.exit(0)
       except Exception:
           print("[Error] Status line failed")
           sys.exit(0)
   
   if __name__ == '__main__':
       main()
   ```

2. **Update `.claude/settings.json`** to use your new status line:
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "uv run .claude/status_lines/your_status_line.py"
     }
   }
   ```

## Input Data Structure

Status line scripts receive JSON input via stdin with session information:

```json
{
  "session_id": "uuid",
  "model": {
    "display_name": "Claude 3 Opus"
  },
  "workspace": {
    "current_dir": "/path/to/project"
  },
  "version": "1.0.92",
  // ... other session data
}
```

## Session Data

Session data is stored in `.claude/data/sessions/{session_id}.json`:

```json
{
  "session_id": "uuid",
  "agent_name": "FLUX",
  "prompts": ["List of user prompts"],
  "extras": {
    "custom_key": "custom_value"
  }
}
```

## Color Codes Reference

| Color | ANSI Code | Usage |
|-------|-----------|-------|
| Red | `\033[31m` | Errors, debug tasks |
| Green | `\033[32m` | Success, creation tasks |
| Yellow | `\033[33m` | Commands, warnings |
| Blue | `\033[34m` | Model names, questions |
| Magenta | `\033[35m` | Refactor tasks |
| Cyan | `\033[36m` | Model names (v1), extras |
| White | `\033[37m` | General text |
| Gray | `\033[90m` | Secondary information |
| Bright Red | `\033[91m` | Agent names |
| Bright White | `\033[97m` | Current/active content |
| Reset | `\033[0m` | Reset to default |

## Tips

- Status lines should fail gracefully and always output something
- Keep status lines concise - terminal width is limited
- Use color coding to make information scannable at a glance
- Log errors for debugging but don't display them in the status line
- Consider truncating long text with ellipsis (...)

## Troubleshooting

If your status line isn't working:

1. Check the logs in `logs/status_line.json`
2. Test your script manually:
   ```bash
   echo '{"session_id":"test","model":{"display_name":"Claude"}}' | uv run .claude/status_lines/your_script.py
   ```
3. Ensure your script has proper error handling
4. Verify the path in `.claude/settings.json` is correct

## Future Enhancements

Consider these ideas for new status lines:
- Token usage tracking
- Time elapsed in session
- Number of tools used
- Current task completion percentage
- Memory usage indicators
- Network status for API calls
- Multi-line status with more information