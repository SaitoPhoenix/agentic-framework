---
name: worktree-permissions
aliases:
  - worktree permissions task
  - worktree_permissions
  - git worktree permissions
entity_classification: technology/task
status: new
created: 2025-10-08T00:00:00Z
last_updated: 2025-10-08T00:00:00Z
source_episodes:
  - 251008_EP_7
summary: A modular task for Claude Code hooks that manages tool-level permissions based on git worktree context and branch type, enforcing workspace boundaries to prevent cross-worktree operations
ambiguities: []
relationships:
  - type: is_part_of
    entity: claude-code-hooks
    description: Worktree permissions is a reusable task component in the hooks system
    role: security component
    source: 251008_EP_7
  - type: designed_by
    entity: yuki
    description: Yuki implemented the worktree permissions task based on Saito's requirements
    role: implementation
    source: 251008_EP_7
  - type: works_with
    entity: security-guard
    description: Runs before security-guard in the pre_tool_use hook to provide two-layer security
    role: complementary task
    source: 251008_EP_7
  - type: uses
    entity: pathspec
    description: Uses pathlib for path resolution and boundary validation
    role: consumer
    source: 251008_EP_7
---

## Facts

### Architecture
- Runs on the pre_tool_use hook before security-guard task [251008_EP_7]
- Only activates when current working directory is inside a git worktree [251008_EP_7]
- Detects worktree context using `git worktree list --porcelain` command [251008_EP_7]
- Extracts branch type from branch name pattern TYPE/name (e.g., feat/new-ui) [251008_EP_7]
- Applies different permission sets based on branch type [251008_EP_7]
- Uses longest-path matching algorithm to identify correct worktree when nested [251008_EP_7]
- Consists of 6 Python modules: main.py, detector.py, config_loader.py, permission_checker.py, path_validator.py, command_splitter.py [251008_EP_7]

### Module Structure
- **main.py**: Entry point that orchestrates permission checking and error handling [251008_EP_7]
- **detector.py**: Detects git worktree context and extracts branch information [251008_EP_7]
- **config_loader.py**: Pydantic-based configuration loading with validation [251008_EP_7]
- **permission_checker.py**: Matches tools against permissions and returns most restrictive decision [251008_EP_7]
- **path_validator.py**: Validates file paths and cd commands stay within worktree boundaries [251008_EP_7]
- **command_splitter.py**: Splits Bash commands by separators while respecting quotes and subshells [251008_EP_7]

### Configuration Structure
- Rules organized by branch type with extensible grouping [251008_EP_7]
- Each permission group includes reason field for decision explanations [251008_EP_7]
- Four permission levels: allow, ask, deny, ignore [251008_EP_7]
- Global rules: always_allow and always_deny lists [251008_EP_7]
- Special handling for main worktree with optional permissions override [251008_EP_7]
- Unknown branch fallback permissions for unrecognized types [251008_EP_7]

### Branch Types (GitHub Flow)
- feat: Feature branches for new functionality [251008_EP_7]
- fix: Bug fix branches [251008_EP_7]
- hotfix: Urgent bug fix branches [251008_EP_7]
- refactor: Code refactoring branches [251008_EP_7]
- perf: Performance improvement branches [251008_EP_7]
- test: Testing branches [251008_EP_7]
- docs: Documentation branches [251008_EP_7]
- chore: Non-code change branches [251008_EP_7]
- build: Build system change branches [251008_EP_7]
- ci: CI/CD pipeline change branches [251008_EP_7]
- security: Security-related change branches [251008_EP_7]
- exp: Experimental branches with permissive permissions [251008_EP_7]

### Permission Decisions
- **ignore**: Returns None, no permission decision made (pass through) [251008_EP_7]
- **allow**: Explicitly allows operation with hookSpecificOutput [251008_EP_7]
- **ask**: Requires user confirmation before proceeding [251008_EP_7]
- **deny**: Blocks the operation with clear reason [251008_EP_7]
- Most restrictive permission wins: deny > ask > allow > ignore [251008_EP_7]

### Special Behaviors
- Read tool always allowed outside worktree boundaries [251008_EP_7]
- cd command always allowed within worktree, always denied outside [251008_EP_7]
- Multiple Bash commands split on separators (&&, ||, |, ;) [251008_EP_7]
- Returns most restrictive permission when multiple commands detected [251008_EP_7]
- Validates cwd exists before processing [251008_EP_7]
- Fails open on errors (never blocks legitimate operations) [251008_EP_7]

### Pattern Matching
- Exact tool match: "Write" matches tool_name "Write" [251008_EP_7]
- Pattern match: "Bash(git push:*)" matches Bash with command starting "git push" [251008_EP_7]
- Generic match: "Bash" matches any Bash command (lowest priority) [251008_EP_7]
- Case-insensitive permission values normalized to lowercase [251008_EP_7]

### Test Coverage
- 16 comprehensive test payloads covering all scenarios [251008_EP_7]
- Tests for main worktree behavior (ignore decision) [251008_EP_7]
- Tests for branch-specific permissions (feat, fix, test, exp) [251008_EP_7]
- Tests for cd command boundary enforcement [251008_EP_7]
- Tests for file operation boundary enforcement [251008_EP_7]
- Tests for multiple command handling [251008_EP_7]
- Tests for global always_allow and always_deny rules [251008_EP_7]
- All tests include permissionDecisionReason validation [251008_EP_7]

## Decisions

- **Tool-level permissions separate from file/command-level security** [251008_EP_7]
  - **Category:** Architecture
  - **Status:** Final
  - **Created:** 2025-10-08
  - **Rationale:** Two-layer security model where worktree permissions handles tool access, security-guard handles granular file/command restrictions
  - **Impact:** Cleaner separation of concerns, worktree permissions focuses on workspace isolation

- **Branch type extracted from branch name pattern TYPE/name** [251008_EP_7]
  - **Category:** Configuration Design
  - **Status:** Final
  - **Created:** 2025-10-08
  - **Rationale:** Aligns with standard git branching conventions (gitflow-style) and is more intuitive than directory naming
  - **Impact:** Permissions follow actual branch semantics rather than worktree directory names

- **Use longest-path matching for worktree detection** [251008_EP_7]
  - **Category:** Implementation
  - **Status:** Final
  - **Created:** 2025-10-08
  - **Rationale:** Correctly identifies linked worktrees when nested inside main repository directory
  - **Impact:** Prevents false matches with main worktree when cwd is in linked worktree subdirectory

- **Extensible branch type grouping in configuration** [251008_EP_7]
  - **Category:** Configuration Design
  - **Status:** Final
  - **Created:** 2025-10-08
  - **Rationale:** Allows multiple branch types to share same permission set, easier to add new types
  - **Impact:** Configuration format: `branch_types: [fix, hotfix]` with shared permissions

- **Read tool exception for boundary enforcement** [251008_EP_7]
  - **Category:** Security Policy
  - **Status:** Final
  - **Created:** 2025-10-08
  - **Rationale:** Developers need to read files outside worktree for context (shared code, docs, config)
  - **Impact:** Read operations never blocked by path boundaries, only by permission level

- **cd command special handling** [251008_EP_7]
  - **Category:** Security Policy
  - **Status:** Final
  - **Created:** 2025-10-08
  - **Rationale:** Workspace isolation requires preventing directory traversal outside worktree
  - **Impact:** cd always allowed within worktree, always denied outside with clear error message

- **Remove prefix from permission reasons** [251008_EP_7]
  - **Category:** User Experience
  - **Status:** Final
  - **Created:** 2025-10-08
  - **Rationale:** Configuration reasons already include "Worktree Permissions:" prefix, adding another in code caused double-prefixing
  - **Impact:** Clean reason strings flow from config directly to response without modification

## Requirements

- **Current working directory must exist** [251008_EP_7]
  - **Category:** Validation
  - **Priority:** Critical
  - **Status:** Fulfilled
  - **Details:** Task validates cwd exists before processing, reports error via systemMessage if show_errors enabled
  - **Created:** 2025-10-08

- **Git worktree commands must be available** [251008_EP_7]
  - **Category:** Environment
  - **Priority:** High
  - **Status:** Active
  - **Details:** Requires git CLI with worktree support for detection to function
  - **Created:** 2025-10-08

## Accomplishments

### Implementation
- Created complete worktree_permissions task structure with 6 Python modules [251008_EP_7]
- Implemented git worktree detection using `git worktree list --porcelain` [251008_EP_7]
- Implemented longest-path matching for accurate worktree identification [251008_EP_7]
- Implemented Bash command splitting with quote and subshell handling [251008_EP_7]
- Implemented path boundary validation with special cd handling [251008_EP_7]
- Implemented most-restrictive permission precedence logic [251008_EP_7]
- Created comprehensive worktree-permissions.yaml configuration [251008_EP_7]
- Updated hooks_config.yaml to include worktree_permissions task [251008_EP_7]
- Created detailed README.md documentation with examples [251008_EP_7]

### Bug Fixes
- Fixed Pydantic validation to accept case-insensitive permission values [251008_EP_7]
- Fixed worktree detection to use longest-path matching instead of first-match [251008_EP_7]
- Fixed graceful error handling for non-existent cwd paths [251008_EP_7]
- Added cwd existence validation before processing [251008_EP_7]
- Fixed double-prefixing of permission reasons [251008_EP_7]

### Testing
- Created 16 comprehensive test payloads for all scenarios [251008_EP_7]
- Successfully tested worktree detection in main and linked worktrees [251008_EP_7]
- Verified branch type extraction from branch names [251008_EP_7]
- Confirmed permission decisions match configuration [251008_EP_7]
- Tested cd command boundary enforcement [251008_EP_7]
- Tested file operation boundary enforcement [251008_EP_7]
- Tested Read tool exception for outside worktree access [251008_EP_7]
- Tested multiple command splitting with most-restrictive logic [251008_EP_7]
- Updated all test payloads with permissionDecisionReason expectations [251008_EP_7]
- All 16 worktree permission tests passing [251008_EP_7]

## Constraints

- **No caching of git worktree list** [251008_EP_7]
  - **Category:** Performance
  - **Status:** Active
  - **Scope:** All tool calls in worktree_permissions task
  - **Reason:** Must run `git worktree list` on every tool call to detect current worktree state
  - **Created:** 2025-10-08

- **Only activates when cwd is inside a worktree** [251008_EP_7]
  - **Category:** Scope
  - **Status:** Active
  - **Scope:** All permission checking logic
  - **Reason:** Worktree permissions only make sense within a git worktree context
  - **Created:** 2025-10-08

## Approaches

### Error Handling
- Fail open philosophy - never block legitimate operations due to bugs [251008_EP_7]
- Graceful error reporting via systemMessage based on show_errors config [251008_EP_7]
- No exceptions raised to standard error, all errors handled internally [251008_EP_7]
- Returns None (pass through) on any processing error [251008_EP_7]

### Path Resolution
- Uses pathlib for robust path operations [251008_EP_7]
- Resolves relative paths to absolute before comparison [251008_EP_7]
- Uses Path.relative_to() for boundary checking [251008_EP_7]
- Handles edge cases like symlinks and normalized paths [251008_EP_7]

### Command Parsing
- Character-by-character parsing for Bash command splitting [251008_EP_7]
- Tracks quote state (single, double, none) [251008_EP_7]
- Tracks subshell depth to avoid splitting inside $() or backticks [251008_EP_7]
- Splits on &&, ||, |, ; only when outside quotes and subshells [251008_EP_7]

### Testing Strategy
- Shell scripts for easy payload execution (.sh files) [251008_EP_7]
- JSON payloads with expected output validation [251008_EP_7]
- Verbose logging enabled for debugging during development [251008_EP_7]
- Iterative testing with fixes applied based on observed behavior [251008_EP_7]

## Philosophies

### Workspace Isolation
- Worktrees should be isolated sandboxes for development [251008_EP_7]
- Operations in worktree should not affect other worktrees or main repo [251008_EP_7]
- Read access allowed outside for context, write operations contained [251008_EP_7]

### Permission Model Design
- Permissions based on branch type reflect development workflow [251008_EP_7]
- Feature branches more permissive for active development [251008_EP_7]
- Test branches restrictive to prevent accidental commits [251008_EP_7]
- Experimental branches highly permissive for exploration [251008_EP_7]

### Configuration Philosophy
- Reasons should explain the "why" behind permission decisions [251008_EP_7]
- Configuration should be self-documenting with clear reason strings [251008_EP_7]
- Extensible design allows easy addition of new branch types [251008_EP_7]

## Patterns

### Two-Layer Security Model
- Worktree permissions checks tool-level access first [251008_EP_7]
- Security-guard checks granular file/command restrictions second [251008_EP_7]
- Both layers can contribute to final permission decision [251008_EP_7]
- Most restrictive decision wins across all layers [251008_EP_7]

### Detection Flow
- Extract cwd from input_data payload [251008_EP_7]
- Validate cwd exists before processing [251008_EP_7]
- Run `git worktree list --porcelain` to get all worktrees [251008_EP_7]
- Find worktree with longest matching path to cwd [251008_EP_7]
- Determine if main worktree (index 0) or linked worktree [251008_EP_7]
- Extract branch name from matched worktree [251008_EP_7]
- Parse branch type from TYPE/name pattern [251008_EP_7]

### Permission Resolution
- Check if main worktree with enabled=false → ignore [251008_EP_7]
- Check always_deny rules → deny immediately [251008_EP_7]
- Check always_allow rules → allow immediately [251008_EP_7]
- Special case cd command → validate boundary [251008_EP_7]
- For Bash tool, split commands and check each → most restrictive [251008_EP_7]
- Match branch type in branch_permissions → use those rules [251008_EP_7]
- Fall back to unknown_branch permissions if type not found [251008_EP_7]
- Fall back to default_permission if tool not in permissions [251008_EP_7]
