# Project Context: Local AI Agent

## Conventions
- Skills are stored as directories under `skills/`
- Every skill must have a `SKILL.md` file with YAML frontmatter
- Subagents should be used for complex, multi-step tasks
- All intermediate work and outputs go to `./workspace/`
- MCP tools provide extended filesystem capabilities

## Available Tools
- **MCP Filesystem Server**: read_file, write_file, list_directory, append_file
- **Planning**: write_todos for breaking down complex tasks
- **Delegation**: task tool for spawning subagents

## Known Entities
- **Main Agent**: Generic orchestrator that plans and delegates
- **Researcher**: Specialized in web search and data aggregation (via SKILL.md)
- **Code Reviewer**: Specialized in code quality analysis (via SKILL.md)

## Workspace Rules
- Always save outputs to `./workspace/`
- Use relative paths from workspace root
- Create descriptive filenames (e.g. `research-topic.md`, `review-filename.md`)
