---
allowed-tools: Read, Bash(eza:*)
description: List all MCP servers with descriptions from their README files
model: claude-3-5-haiku-latest
---

List all MCP servers using this command: `eza --tree --level=1 {{args.0|default:"/mnt/e/DataAlchemy/Repositories/mcp/servers"}}`

For each MCP server found:
1. Read the README.md file
2. Extract a concise, single-sentence description of what the MCP server does

Output the results in the following format:

## Available MCP Servers

| Server Name | Description |
|-------------|-------------|
| [server-name] | [Single-sentence description of the server's purpose and functionality] |

Requirements:
- List servers in alphabetical order by name
- Keep descriptions to one sentence (max 100 characters)
- If no README.md exists, note "No description available"
- Only include directories that appear to be MCP servers (contain server-related files)
- Skip any directories that are clearly not MCP servers (e.g., .git, node_modules, etc.)

If the specified directory doesn't exist or contains no MCP servers, clearly indicate this to the user.