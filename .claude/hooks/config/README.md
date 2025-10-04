# Claude Code Hooks Configuration

This directory contains the configuration for Claude Code hooks.

## Table of Contents

- [Hooks System Overview](#hooks-system-overview)
- [Available Tasks](#available-tasks)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Configuration Reference](#configuration-reference)

## Hooks System Overview

Hooks are callbacks that run at specific points in Claude Code's lifecycle. Each hook can execute multiple tasks sequentially. If a task fails, other tasks continue to run (failures are isolated).

**For detailed information on hook types and when they fire, see:**
https://docs.claude.com/en/docs/claude-code/hooks

### Hook Execution

- Tasks run **sequentially** in the order defined
- Failed tasks don't stop subsequent tasks
- Each task receives `input_data` (hook-specific) and `global_config`

### Input Data

Each hook provides different data in the `input_data` parameter. See the [official hooks documentation](https://docs.claude.com/en/docs/claude-code/hooks) for details on what data is available for each hook type.

### Environment Variables

For API-based providers, set these environment variables in your `.env` file:

| Variable | Provider | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | OpenAI | TTS and LLM services |
| `ANTHROPIC_API_KEY` | Anthropic | LLM services |
| `GCLOUDTTS_SERVICE_KEY` | Google Cloud | TTS services |
| `ELEVENLABS_API_KEY` | ElevenLabs | TTS services |
| `TABBY_API_KEY` | Tabby | LLM services |
| `OLLAMA_API_KEY` | Ollama | LLM services |

**Note:** Only set the API keys for providers you're actually using.

## Available Tasks

Tasks are reusable components that can be attached to any hook. Each task performs a specific function and can be configured independently.

### 1. log_hook

**Purpose:** Logs hook input data to JSON files for debugging and analysis

**Module:** `log_hook.main`
**Function:** `log_hook_data`

**Use Cases:**
- Debugging hooks and understanding data flow
- Auditing hook activity
- Analyzing input data for custom task development

**Output:** Appends to `{log_directory}/{hook_name}.json`

**Error Handling:** Fails silently unless `verbose_errors` is true

**Config:**

```yaml
hook_name: (string, required)
  # Name of the hook (used for log filename)
  # Example: "stop", "user_prompt_submit"
```

---

### 2. tts_notification

**Purpose:** Announces completion messages using text-to-speech

**Module:** `tts_notification.main`
**Function:** `announce_tts`

**Use Cases:**
- Audio feedback when Claude finishes tasks
- Accessibility features
- Ambient awareness of task completion

**Output:** Plays audio through the configured TTS provider

**Error Handling:** Fails silently unless `verbose_errors` is true

**Config:**

```yaml
tts: (object, required)
  provider: (string)
    # TTS provider: openai, gcloud, elevenlabs, pyttsx3

  voice: (string)
    # Voice identifier (provider-specific)
    # Examples:
    #   openai: "alloy", "echo", "fable", "onyx", "nova", "shimmer"
    #   gcloud: "en-US-Wavenet-F", "en-US-Chirp3-HD-Despina"
    #   elevenlabs: "WejK3H1m7MI9CHnIjW9K", "fUjY9K2nAIwlALOwSiwc"

  model: (string, optional)
    # Model identifier (openai/elevenlabs only)
    # Examples:
    #   elevenlabs: "eleven_turbo_v2_5", "eleven_multilingual_v2"
    #   openai: "gpt-4o-mini-tts", "gpt-4o-audio-preview"

llm: (object, optional)
  # If omitted, uses rendered pattern directly without LLM processing

  provider: (string)
    # LLM provider: openai, anthropic, ollama, tabby

  model: (string)
    # Model identifier
    # Examples:
    #   openai: "gpt-4o-mini", "gpt-5"
    #   anthropic: "claude-3-5-haiku-latest"
    #   ollama: "gpt-oss:20b"

  base_url: (string, optional)
    # Custom API endpoint for local providers

message_pattern: (string, optional)
  # Jinja2 template file in .claude/hooks/utils/patterns/
  # Default: "completion_message.j2"
  # Pattern files can use {{ user_name }} and other variables

choose_random: (boolean, optional)
  # If true, renders template twice:
  #   1. First to select random message
  #   2. Then to replace variables
  # Default: false

user_name: (string, optional)
  # User's name for {{ user_name }} placeholder in templates
```

---

### 3. conversation_capture

**Purpose:** Captures conversation transcripts to structured episodic memory files

**Module:** `conversation_capture.main`
**Function:** `start_conversation_capture`

**Use Cases:**
- Building conversation history for memory systems
- Creating training data
- Maintaining episodic memory for agent architectures

**Output:** Creates subprocess that watches transcript and writes to:
`{episodic_path}/{YYYY}/{MM}/{YYMMDD}_EP_{N}.json`

**Error Handling:** Prints errors to stderr

**Config:**

```yaml
pid_file_name: (string, required)
  # PID file name for watchdog process
  # Default: "conversation_watchdog.pid"
  # Stored in: .claude/hooks/pid/{session_id}/{pid_file_name}

episodic_path: (string, required)
  # Base directory for memory files (relative to project root)
  # Example: ".claude/agents/memory/episodic"

human_name: (string, required)
  # Human participant name in conversation

agent_name: (string, required)
  # AI agent name in conversation
```

---

### 4. cleanup_subprocesses

**Purpose:** Terminates all running subprocesses for the current session

**Module:** `cleanup_subprocesses.main`
**Function:** `cleanup_subprocesses`

**Use Cases:**
- Session cleanup
- Preventing orphaned processes
- Graceful shutdown of background tasks

**Output:** Sends SIGTERM to processes, removes PID files, cleans up directories

**Error Handling:** Prints errors to stderr, continues on permission errors

**Config:** (none - automatically uses `session_id` from `input_data`)

---

### 5. security_guard

**Purpose:** Prevents accidental exposure of sensitive files and execution of dangerous commands

**Module:** `security_guard.main`
**Function:** `check_security`

**Use Cases:**
- Blocking access to `.env` files and other sensitive data
- Preventing dangerous bash commands (rm -rf, sudo, etc.)
- Enforcing security policies through configurable rules
- Validating security rules on session start

**Output:** Returns permission decision (allow/ask/deny) via `hookSpecificOutput`

**Error Handling:** Fails safely (allows on error) unless `verbose_errors` is true

**Config:**

```yaml
rules_file: (string, required)
  # Path to security-rules.yaml (relative to project root)
  # Default: ".claude/hooks/config/security-rules.yaml"
  # Contains whitelist/blacklist rules for files and commands

validate_only: (boolean, optional)
  # If true, only validate rules and exit (for session_start)
  # If false, perform security checks (for pre_tool_use)
  # Default: false
```

**Security Rules Structure:**

The `security-rules.yaml` file defines rules in a whitelist/blacklist hierarchy:

```yaml
# Whitelist (processed first, highest precedence)
whitelist:
  allow/ask/deny:
    files:
      - pattern: (string, required) # Gitignore-style pattern
        message: (string, optional) # Custom message
        tools: (list, optional)     # Specific tools [Read, Write, Edit, MultiEdit, Bash]

    commands:
      - command: (string, required)      # Base command (e.g., "rm", "sudo")
        block_always: (boolean, optional) # Block regardless of flags/paths/patterns
        flags: (list, optional)           # List of flag combinations [["-rf"], ["--force"]]
        paths: (list, optional)           # Literal path arguments ["/", "~", ".", "*"]
        patterns: (list, optional)        # Regex patterns ["\\s\\./", "\\|\\s*sh"]
        message: (string, optional)       # Custom message
        tools: (list, optional)           # Specific tools (default: all tools)

# Notes:
# - paths: Matched as exact literal arguments (e.g., "/" matches "rm -rf /" only)
# - patterns: Matched as regex against full command (for advanced matching)
# - Multiple conditions use AND logic (all must match)

# Blacklist (processed after whitelist)
blacklist:
  allow/ask/deny:
    # Same structure as whitelist
```

**File Pattern Examples:**
- `.env` - Blocks .env in current directory
- `**/.env` - Blocks .env anywhere in tree
- `*.pem` - Blocks all PEM files
- `.env.example` - Whitelist allows template files

**Command Rule Matching Logic:**

Commands are matched using **AND logic** when multiple conditions are specified:

1. **Base command** must match (e.g., "rm", "sudo")
2. **All specified conditions** must match:
   - If `block_always: true` → Always match
   - If `flags` specified → Command must have those flags
   - If `paths` specified → Command must have those **exact literal paths** as arguments
   - If `patterns` specified → Command must match those **regex patterns**
   - If `flags` AND `paths` both specified → Command must have BOTH

**Path Matching:**
- Paths are matched as **literal arguments only**
- `/` matches `rm -rf /` but NOT `rm -rf a/b` (no substring matching)
- Use `patterns` for advanced matching like `["\\./.*"]` to match any `./` path

**Command Rule Examples:**
- `command: "sudo"` with `block_always: true`
  - Matches: `sudo apt install`, `sudo rm`
  - Does NOT match: `rm`, `curl`

- `command: "rm"` with `flags: [["-rf"]]` and `paths: ["/", "~", ".", "*"]`
  - Matches: `rm -rf /`, `rm -rf .`, `rm -rf *` (exact literal argument match)
  - Does NOT match: `rm -rf a/b`, `rm -rf ./file`, `rm -rf a/*` (not exact matches)

- `command: "rm"` with `flags: [["-rf"]]` and `patterns: ["\\s\\./"]`
  - Matches: `rm -rf ./anything`, `rm -rf ././c` (regex pattern match)
  - Does NOT match: `rm -rf /path`, `rm -rf a/b`

- `command: "curl"` with `patterns: ["\\|\\s*sh"]`
  - Matches: `curl url | sh`, `curl url | bash`
  - Does NOT match: `curl url > file`

- `command: "echo"` with no conditions
  - Matches: Any echo command

**Permission Levels:**
- `deny` - Block the action completely (exit code 2)
- `ask` - Prompt user for confirmation (exit code 1)
- `allow` - Allow but log the action (exit code 0)

**Rule Precedence:**
1. Whitelist rules (highest priority)
2. Blacklist rules
3. Within each list: deny > ask > allow (most restrictive wins)
4. If whitelist matches, blacklist is ignored
5. If no rules match, allow by default

---

## Usage Examples

### Example 1: Simple TTS notification without LLM

Uses pattern text directly without LLM processing. Great for fast, local announcements.

```yaml
stop:
  tts_notification:
    enabled: true
    module: "tts_notification.main"
    function: "announce_tts"
    config:
      tts:
        provider: "pyttsx3"  # Local TTS, no API key needed
      message_pattern: "pregenerated_completion_messages.j2"
      choose_random: true
      user_name: "Alex"
```

### Example 2: TTS with LLM-generated creative messages

Uses an LLM to generate varied, contextual completion messages.

```yaml
stop:
  tts_notification:
    enabled: true
    module: "tts_notification.main"
    function: "announce_tts"
    config:
      tts:
        provider: "openai"
        voice: "nova"
        model: "gpt-4o-mini-tts"
      llm:
        provider: "anthropic"
        model: "claude-3-5-haiku-latest"
      message_pattern: "completion_message.j2"
      user_name: "Alex"
```

### Example 3: Multiple tasks on one hook

You can attach multiple tasks to a single hook. They run sequentially.

```yaml
session_start:
  log_hook:
    enabled: true
    module: "log_hook.main"
    function: "log_hook_data"
    config:
      hook_name: "session_start"

  conversation_capture:
    enabled: true
    module: "conversation_capture.main"
    function: "start_conversation_capture"
    config:
      episodic_path: ".claude/agents/memory/episodic"
      human_name: "Alex"
      agent_name: "Claude"
```

### Example 4: Security guard for pre_tool_use

Prevent accidental exposure of sensitive files and dangerous commands.

```yaml
pre_tool_use:
  security_guard:
    enabled: true
    module: "security_guard.main"
    function: "check_security"
    config:
      rules_file: ".claude/hooks/config/security-rules.yaml"
      validate_only: false
```

### Example 5: Security rules validation on session start

Validate security rules when session starts to catch configuration errors early.

```yaml
session_start:
  security_guard_validator:
    enabled: true
    module: "security_guard.main"
    function: "check_security"
    config:
      rules_file: ".claude/hooks/config/security-rules.yaml"
      validate_only: true
```

### Example 6: Disable a task

Set `enabled: false` to disable a task without removing its configuration.

```yaml
stop:
  tts_notification:
    enabled: false  # Task will not run
    module: "tts_notification.main"
    function: "announce_tts"
    config:
      # ... config preserved for future use
```

---

## Troubleshooting

### TTS not playing audio

**Symptoms:** No audio plays when hooks fire

**Solutions:**
- Check that the API key for your provider is set in `.env`
- Verify the voice ID is valid for your provider
- Set `verbose_errors: true` in global config to see error messages
- Test the provider directly: `uv run .claude/hooks/utils/tts/tts-cli.py --provider <provider> --voice <voice> "test message"`

---

### LLM not generating messages

**Symptoms:** TTS falls back to pattern text or fails silently

**Solutions:**
- Check that the API key is set in `.env`
- Verify model name is correct for your provider
- Increase `subprocess_timeout` if the LLM is slow (default: 10 seconds)
- Set `verbose_errors: true` to see error messages
- Test the LLM directly: `uv run .claude/hooks/utils/llm/llm_cli.py <provider> <model> "test prompt"`

---

### Hook not running

**Symptoms:** Expected task doesn't execute

**Solutions:**
- Check that `enabled: true` is set for the task
- Verify the hook name matches Claude Code's hook names (see [official docs](https://docs.claude.com/en/docs/claude-code/hooks))
- Check logs in `{log_directory}/` if `log_hook` is enabled
- Set `verbose_errors: true` to see error output

---

### Pattern file not found

**Symptoms:** Error message about missing template file

**Solutions:**
- Pattern files must be in `.claude/hooks/utils/patterns/`
- Check that the filename matches exactly (case-sensitive)
- Verify the file has `.j2` extension
- List available patterns: `ls .claude/hooks/utils/patterns/`

---

### Conversation capture not working

**Symptoms:** No episodic memory files created

**Solutions:**
- Check that `transcript_path` is provided in `input_data` (automatic for `session_start`)
- Verify `episodic_path` directory is writable
- Check for watchdog PID file in `.claude/hooks/pid/{session_id}/`
- Look for error messages in stderr output

---

### Subprocesses not cleaning up

**Symptoms:** Orphaned processes remain after session ends

**Solutions:**
- Verify `cleanup_subprocesses` is enabled on `session_end` hook
- Check PID files in `.claude/hooks/pid/{session_id}/`
- May need to manually kill processes if session crashes: `ps aux | grep conversation_watchdog`
- Remove stale PID files: `rm -rf .claude/hooks/pid/{session_id}/`

---

### Security rules validation failed

**Symptoms:** Error message on session start about invalid security rules

**Solutions:**
- Check the error message for specific validation issues
- Verify YAML syntax in `.claude/hooks/config/security-rules.yaml`
- Ensure all required fields are present:
  - File rules need `pattern`
  - Command rules need `command`
- Check that permission levels are valid: `allow`, `ask`, or `deny`
- Verify tool names are valid: `Read`, `Write`, `Edit`, `MultiEdit`, `Bash`
- Test YAML parsing: `python -c "import yaml; yaml.safe_load(open('.claude/hooks/config/security-rules.yaml'))"`

---

### Security guard blocking legitimate operations

**Symptoms:** Tool calls are blocked unexpectedly

**Solutions:**
- Check which rule is matching in the error message
- Add whitelist rules to override blacklist for specific cases
- Use `ask` permission instead of `deny` for questionable operations
- Adjust file patterns to be more specific (e.g., `.env` vs `**/.env`)
- Set `verbose_errors: true` to see detailed matching information
- Temporarily disable: set `security_guard.enabled: false` in hooks_config.yaml

---

### Security guard not blocking dangerous operations

**Symptoms:** Expected dangerous commands/files are not blocked

**Solutions:**
- Verify `security_guard` is enabled on `pre_tool_use` hook
- Check that rules file path is correct in config
- Ensure rule patterns match the actual file paths/commands
- Test patterns manually with `pathspec` library
- Enable logging to see what rules are being checked
- Verify permission level is `deny` or `ask`, not `allow`

---

### Debugging Tips

**General debugging workflow:**

1. **Enable verbose errors:**
   ```yaml
   global:
     verbose_errors: true
   ```

2. **Enable log_hook on all hooks:**
   ```yaml
   stop:
     log_hook:
       enabled: true
       module: "log_hook.main"
       function: "log_hook_data"
       config:
         hook_name: "stop"
   ```

3. **Check log files:**
   ```bash
   cat logs/stop.json | jq .
   ```

4. **Run hook scripts directly from command line:**
   ```bash
   echo '{"test": "data"}' | uv run .claude/hooks/hook_entry.py --hook stop
   ```

5. **Check stderr output:**
   Run Claude Code from terminal to see stderr output directly

---

## Configuration Reference

The main configuration file is `hooks_config.yaml` in this directory.

### Global Settings

```yaml
global:
  log_directory: (string)
    # Directory for log files (relative to project root)
    # Default: "logs"

  subprocess_timeout: (integer)
    # Timeout for subprocess calls in seconds
    # Affects LLM and TTS CLI calls
    # Default: 10

  verbose_errors: (boolean)
    # Show detailed error messages to stderr
    # Useful for debugging
    # Set to false in production to suppress error output
    # Default: false
```

### Hook Structure

Each hook follows this structure:

```yaml
hook_name:
  task_name:
    enabled: (boolean)
      # Enable or disable this task

    module: (string)
      # Python module path (e.g., "log_hook.main")

    function: (string)
      # Function name to call (e.g., "log_hook_data")

    config: (object)
      # Task-specific configuration
      # See "Available Tasks" section for details
```

### Available Hooks

| Hook Name | When It Fires |
|-----------|---------------|
| `stop` | When Claude Code finishes responding |
| `notification` | When Claude sends notifications |
| `subagent_stop` | When subagent tasks complete |
| `user_prompt_submit` | When user submits a prompt |
| `pre_tool_use` | Before tool calls |
| `post_tool_use` | After tool calls complete |
| `pre_compact` | Before context compaction |
| `session_start` | When session starts/resumes |
| `session_end` | When session ends |

For detailed information about what data is available in each hook, see:
https://docs.claude.com/en/docs/claude-code/hooks

---

## Additional Resources

- **Official Hooks Documentation:** https://docs.claude.com/en/docs/claude-code/hooks
- **Pattern Files:** `.claude/hooks/utils/patterns/`
- **TTS CLI:** `.claude/hooks/utils/tts/tts-cli.py`
- **LLM CLI:** `.claude/hooks/utils/llm/llm_cli.py`
- **Log Files:** `logs/` (or configured `log_directory`)
- **PID Files:** `.claude/hooks/pid/{session_id}/`
