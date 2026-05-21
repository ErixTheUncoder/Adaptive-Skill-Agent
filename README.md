# Local AI Agent with MCP + SKILL.md

A local AI agent that dynamically connects with MCP servers and SKILL.md files using LangChain and Google Gemini.

## Features

- **MCP Integration**: Connect to local MCP servers via stdio transport
- **Dynamic SKILL.md Loading**: Drop new skills into `skills/` folder - agent discovers them automatically
- **File Operations**: Read, write, list, and append files via MCP filesystem server
- **Mock Mode**: Test agent loop without API calls (zero cost)
- **Google Gemini**: Uses free tier Gemini models

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key (optional - skip for mock mode)
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# 3. Run in mock mode (no API needed)
python agent.py --mock

# 4. Run with real Gemini API
python agent.py
```

## Project Structure

```
my-ai-agent/
├── agent.py                    # Main agent script
├── requirements.txt            # Python dependencies
├── AGENTS.md                   # Shared conventions for agent
├── .env.example                # API key template
├── .gitignore                  # Git ignore rules
├── mcp_servers/
│   └── filesystem_server.py    # MCP filesystem server (4 tools)
├── skills/
│   ├── research/
│   │   └── SKILL.md            # Web research skill
│   └── code-reviewer/
│       └── SKILL.md            # Code review skill
└── workspace/                  # Agent file workspace
```

## Usage

### Mock Mode (No API Key Required)

```bash
python agent.py --mock
```

Mock mode simulates the agent loop locally. Try these commands:
- `list files` - Lists workspace directory
- `create a file` - Creates a test file
- `read the file` - Reads a file

### Real Mode (Uses Gemini API)

```bash
python agent.py
```

Requires `GOOGLE_API_KEY` in `.env` file.

## Adding New Skills

Create a new folder in `skills/` with a `SKILL.md` file:

```bash
mkdir -p skills/my-skill
```

```markdown
---
name: my-skill
description: Description of what this skill does. When to use it.
license: MIT
---

# My Skill

## Instructions
1. Step one
2. Step two
```

The agent automatically discovers and uses new skills on next run.

## Adding MCP Servers

Add new MCP server scripts to `mcp_servers/` and update `agent.py`:

```python
# In get_mcp_tools():
client = MultiServerMCPClient({
    "filesystem": {...},
    "my-new-server": {
        "transport": "stdio",
        "command": "python",
        "args": ["mcp_servers/my_server.py"],
    }
})
```

## Configuration

| File | Purpose |
|------|---------|
| `.env` | API keys (GOOGLE_API_KEY) |
| `AGENTS.md` | Shared conventions loaded into system prompt |
| `skills/*/SKILL.md` | Skill definitions with YAML frontmatter |

## API Quotas

| Model | Free Tier Limit |
|-------|----------------|
| gemini-2.5-flash | 20 requests/day |
| gemini-2.5-flash-lite | 1000 requests/day |
| gemini-2.0-flash | Varies |

Use `--mock` mode for unlimited testing without API calls.

## Dependencies

- `deepagents` - LangChain deep agent framework
- `langchain-mcp-adapters` - MCP server integration
- `langchain-google-genai` - Google Gemini API
- `mcp` - MCP protocol implementation
- `python-dotenv` - Environment variable loading

## License

MIT
