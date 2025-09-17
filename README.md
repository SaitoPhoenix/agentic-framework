# Spec-Driven Agentic Development Framework

A comprehensive Claude Code framework that enables spec-driven development using specialized AI agents orchestrated by a team leader agent.

## Installation & Requirements

### Prerequisites
- Claude Code CLI installed and configured
- Python 3.11+ with `uv` package manager
- Git repository initialized
- Unix-like environment (Linux, macOS, WSL)

### Setup
1. Clone this repository into your project
2. Ensure `.claude/` directory is at your project root
3. Configure hooks in `.claude/hooks/config/hooks_config.yaml`

## Getting Started

### Quick Start Workflow
1. **Initialize Project Understanding**: Run `/prime` to analyze your codebase
2. **Create Specifications**: Use `/solution-architect` to generate project specs
3. **Execute Development**: Launch specialized agents for implementation
4. **Review & Iterate**: Use review agents to validate work

### Basic Example
```bash
# Analyze project structure
/prime

# Create a feature specification
/solution-architect create product

# Launch development agent for implementation
# The agent will work in an isolated worktree
/dev-new feature-name
```

## Core Architecture

The framework operates through a **team leader** agent that orchestrates specialized worker agents, each operating in isolated worktrees with configurable permissions. Projects begin with specification generation and create execution plans for specialized agents.

## Available Agents

### Development & Review Agents
- **meta-agent**: Creates and manages new agent definitions
- **code-review-agent**: Senior code reviewer for pull requests and feature validation
- **feature_analyzer**: Evaluates feature implementations against specifications
- **python-code-reviewer**: Python-specific code quality evaluator
- **schema-validation-specialist**: Handles data validation and type safety

### Infrastructure Agents
- **create_worktree**: Sets up isolated git worktrees for agent development
- **cleanup-agent-env**: Manages worktree cleanup and branch removal
- **pr-writer**: Creates well-structured pull requests with comprehensive descriptions
- **claude-configuration-dev**: Develops Claude Code features (hooks, styles, commands)

### Analysis & Discovery Agents
- **codebase-cartographer**: Scans codebases to identify areas for new agents
- **systems-detective**: Reverse engineers codebases for reimplementation
- **simple-summary**: Provides concise bullet-point file summaries

### Subject Matter Expert (SME) Agents
- **sme_ai-ml-platform-architect**: AI/ML platform architecture and LLM integration
- **sme_data-knowledge-graph-architect**: Graph databases and knowledge representation
- **sme_distributed-systems-pipeline-engineer**: Event-driven architecture and ML operations
- **sme_engagement-analytics-developer**: Gamification and behavioral analytics
- **sme_speech-audio-systems-engineer**: Audio processing and speech-to-text pipelines

## Slash Commands

### Project Analysis
- `/prime` - Comprehensive project analysis and understanding
- `/git_status` - Display current git repository status
- `/all_tools` - List all available Claude Code tools
- `/list_available_mcp` - Show available MCP server connections

### Development Workflow
- `/solution-architect [mode] [spec-type]` - Create/update solution specifications
- `/dev-new` - Start new feature development in isolated worktree
- `/dev-current` - Continue development in current context
- `/agent_name` - For prompt testing: Determines the agent that would be used based on the description
- `/update_status_line` - Refresh terminal status display

## Key Directories

### `.claude/patterns/` - Template System (Core Framework)
- `agents/` - Templates for creating specialized AI agents
- `guidelines/` - Standards and best practices templates for agent workflows
- `reports/` - Report format templates (developer vs evaluator styles)
- `rubrics/` - Evaluation criteria templates for agent work quality
- `specs/` - Project specification templates for solution architect workflows
- `usage-docs/` - Documentation templates for feature usage instructions

### `.claude/agents/` - Specialized Agents & Outputs
- Root contains agent definition files (`.md` format)
- `guidelines/` - Agent-specific workflow standards (created by agents)
- `reports/` - Generated evaluation reports (used by developer agents)
- `rubrics/` - Quality assessment criteria (used for work evaluation)
- `usage-docs/` - Feature documentation (created by developer agents)

### `.claude/hooks/` - Lifecycle Event Handlers
- Root Python files for each Claude Code hook type
- `config/` - Hook configuration with on/off switches and worktree permissions
- `utils/` - Shared utilities for hook functionality

### `.claude/commands/` - Custom Slash Commands
- Project analysis and orchestration commands

### `.claude/output-styles/` - Response Formatting
- Custom output format configurations

### `.claude/status_lines/` - Terminal Status Displays
- Real-time session and context information

## Agent Patterns

The framework provides several agent patterns for different use cases:

### Pattern Types
- **basic-agent**: Simple task-focused agents with minimal configuration
- **conversational-expert**: SME agents providing domain expertise through dialogue
- **developer-agent**: Full-featured development agents with comprehensive toolsets
- **evaluator-agent**: Review and validation agents with assessment capabilities
- **basic-identity-agent**: Lightweight agents with defined personas

Each pattern provides a structured template ensuring consistency while allowing customization for specific domains and requirements.

## Hooks System

The framework includes a comprehensive hooks system for lifecycle automation:

### Configuration
Hooks are configured in `.claude/hooks/config/hooks_config.yaml` with:
- Enable/disable switches for each hook
- Custom parameters for hook behavior
- Integration with TTS and LLM utilities

## Worktree Permissions System

The `hooks/config/` contains worktree permissions that control agent tool access (allow/ask/deny) based on their role. Example: review agents in review worktrees can only read files, not write them.

## Agent Workflow

1. **Solution Architect** generates specifications using spec patterns
2. **Team Leader** creates execution plan and spawns specialized agents
4. **Worker Agents** operate in configured worktrees with role-based permissions
3. **Agents** follow guidelines, create reports, and generate usage documentation
5. **Reports** inform subsequent agents for coordinated development

The framework ensures consistency through the patterns system while enabling flexible, permission-controlled agent collaboration.