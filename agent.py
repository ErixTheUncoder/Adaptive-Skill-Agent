import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

load_dotenv()

PROJECT_ROOT = Path(__file__).parent.resolve()
MCP_SERVER = str(PROJECT_ROOT / "mcp_servers" / "filesystem_server.py")


def load_skills(skills_dir):
    """Load skill metadata from SKILL.md files."""
    skills = []
    skills_path = Path(skills_dir)
    if not skills_path.exists():
        return skills
    
    for skill_dir in skills_path.iterdir():
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            content = skill_file.read_text()
            if content.startswith("---"):
                end = content.find("---", 3)
                if end != -1:
                    frontmatter = content[3:end].strip()
                    body = content[end+3:].strip()
                    name = ""
                    description = ""
                    for line in frontmatter.split("\n"):
                        if line.startswith("name:"):
                            name = line.split(":", 1)[1].strip()
                        elif line.startswith("description:"):
                            description = line.split(":", 1)[1].strip()
                    skills.append({
                        "name": name,
                        "description": description,
                        "path": str(skill_file),
                        "body": body
                    })
    return skills


async def get_mcp_tools():
    client = MultiServerMCPClient({
        "filesystem": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [MCP_SERVER],
        }
    })
    return await client.get_tools()


def create_mock_agent(mcp_tools):
    """Create a mock agent that simulates tool calls without using API quota."""
    skills = load_skills(PROJECT_ROOT / "skills")
    skills_text = "\n".join([f"- {s['name']}: {s['description']}" for s in skills])

    system_prompt = f"""You are a helpful AI assistant with access to filesystem tools.

Available Skills:
{skills_text}

When you need to use a skill, read its full instructions first using the read_file tool.

Always save outputs to the ./workspace/ directory."""

    # Create a mock model that responds to tool calls
    class MockModel:
        """Mock model that simulates LLM behavior for testing."""
        
        def __init__(self, tools):
            self.tools = tools
            self.call_count = 0
        
        async def ainvoke(self, messages):
            self.call_count += 1
            last_msg = messages[-1]
            
            # Check if this is a tool result (ToolMessage)
            is_tool_result = any(isinstance(m, ToolMessage) for m in messages)
            
            if is_tool_result:
                # After getting tool result, provide a final answer
                return AIMessage(
                    content="Based on the tool output, here's what I found:\n\n" + str(last_msg.content)
                )
            
            # Get the user's original query (skip the system prompt part)
            user_query = last_msg.content
            if "User: " in user_query:
                user_query = user_query.split("User: ", 1)[1]
            
            query_lower = user_query.lower()
            
            # Check if user wants to list/show files
            if any(keyword in query_lower for keyword in ["list files", "show files", "what files", "show me what files", "directory contents"]):
                return AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "list_directory",
                        "args": {"path": "."},
                        "id": f"mock-call-{self.call_count}"
                    }]
                )
            
            # Check if user wants to create/write a file
            if any(keyword in query_lower for keyword in ["create a file", "write a file", "make a file", "create file"]):
                return AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "write_file",
                        "args": {"path": "workspace/test.txt", "content": "Mock test content"},
                        "id": f"mock-call-{self.call_count}"
                    }]
                )
            
            # Check if user wants to read a file
            if any(keyword in query_lower for keyword in ["read the file", "read file", "open file", "view file"]):
                return AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "read_file",
                        "args": {"path": "workspace/test.txt"},
                        "id": f"mock-call-{self.call_count}"
                    }]
                )
            
            # Default: respond normally
            return AIMessage(
                content=f"[MOCK MODE] I received: '{user_query[:60]}...'\n\n"
                        f"In mock mode, I can simulate tool calls. Try:\n"
                        f"- 'list files' - calls list_directory tool\n"
                        f"- 'create a file' - calls write_file tool\n"
                        f"- 'read the file' - calls read_file tool\n\n"
                        f"This demonstrates the agent loop without using API quota!"
            )
        
        def bind_tools(self, tools):
            """Mock bind_tools - just return self."""
            return self

    return MockModel(mcp_tools), mcp_tools, system_prompt


def create_agent(mcp_tools):
    """Create a real agent using Gemini."""
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
    )

    skills = load_skills(PROJECT_ROOT / "skills")
    skills_text = "\n".join([f"- {s['name']}: {s['description']}" for s in skills])

    system_prompt = f"""You are a helpful AI assistant with access to filesystem tools.

Available Skills:
{skills_text}

When you need to use a skill, read its full instructions first using the read_file tool.

Always save outputs to the ./workspace/ directory.

IMPORTANT: After using tools, provide a final answer to the user. Do NOT keep calling the same tool repeatedly. Once you have the information you need, respond with a clear answer."""

    model_with_tools = model.bind_tools(mcp_tools)
    
    return model_with_tools, mcp_tools, system_prompt


async def run_agent(model_with_tools, tools, system_prompt, user_input):
    """Manual ReAct loop that works with both real and mock models."""
    messages = [
        HumanMessage(content=f"System: {system_prompt}\n\nUser: {user_input}")
    ]
    
    max_iterations = 5
    for i in range(max_iterations):
        response = await model_with_tools.ainvoke(messages)
        
        # Check if there are tool calls
        tool_calls = getattr(response, "tool_calls", [])
        content = response.content
        
        if not tool_calls:
            # No more tool calls - return the final response
            return content
        
        # Execute tool calls
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            
            print(f"  [Tool call {i+1}] Calling: {tool_name}({tool_args})")
            
            # Find and execute the tool
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                try:
                    tool_result = await tool.ainvoke(tool_args)
                    # Extract text from MCP result format
                    if isinstance(tool_result, dict):
                        tool_result = tool_result.get("text", str(tool_result))
                    elif isinstance(tool_result, list):
                        # Handle list of content blocks
                        text_parts = []
                        for block in tool_result:
                            if isinstance(block, dict):
                                text_parts.append(block.get("text", str(block)))
                            else:
                                text_parts.append(str(block))
                        tool_result = "\n".join(text_parts)
                    print(f"  [Tool result] {str(tool_result)[:100]}")
                except Exception as e:
                    tool_result = f"Error: {e}"
                    print(f"  [Tool error] {e}")
            else:
                tool_result = f"Error: Tool '{tool_name}' not found"
            
            messages.append(ToolMessage(content=tool_result, tool_call_id=tool_id))
    
    return "Agent reached maximum iterations without completing the task."


async def main(mock=False):
    print("Loading MCP tools...")
    mcp_tools = await get_mcp_tools()
    print(f"Loaded {len(mcp_tools)} MCP tools: {[t.name for t in mcp_tools]}")

    if mock:
        model_with_tools, tools, system_prompt = create_mock_agent(mcp_tools)
        print("\n=== Adaptive-Skill-Agent (MOCK MODE - No API calls) ===")
    else:
        model_with_tools, tools, system_prompt = create_agent(mcp_tools)
        print("\n=== Adaptive-Skill-Agent (Gemini 2.0 Flash) ===")
    
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        print("\nAgent is thinking...")

        try:
            response = await run_agent(model_with_tools, tools, system_prompt, user_input)
            
            # Handle response format
            if isinstance(response, dict):
                response = response.get("text", str(response))
            elif isinstance(response, list):
                text_parts = []
                for block in response:
                    if isinstance(block, dict):
                        text_parts.append(block.get("text", str(block)))
                    else:
                        text_parts.append(str(block))
                response = "\n".join(text_parts)
            
            print(f"\nAgent: {response}\n")
            print("-" * 50)

        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
            print("-" * 50)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Use mock model (no API calls)")
    args = parser.parse_args()
    asyncio.run(main(mock=args.mock))
