# Adaptive-Skill-Agent

A local AI agent that dynamically discovers and loads SKILL.md files and MCP servers at runtime. Built with LangChain and Google Gemini.

## Features

- **Dynamic Skill Discovery**: Drop new `SKILL.md` files into `skills/` - agent auto-discovers them
- **MCP Integration**: Connect to local MCP servers via stdio transport
- **File Operations**: Read, write, list, and append files via MCP filesystem server
- **Mock Mode**: Test the full agent loop without API calls (zero cost)
- **Google Gemini**: Uses free tier Gemini models
- **Extensible**: Add new skills and MCP servers without changing code

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/erichong/Adaptive-Skill-Agent.git
cd Adaptive-Skill-Agent
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
Adaptive-Skill-Agent/
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
