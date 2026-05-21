from mcp.server.fastmcp import FastMCP
import os
from pathlib import Path

mcp = FastMCP("Filesystem")

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "workspace"))


@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a file in the workspace.

    Args:
        path: Relative path from workspace root (e.g. 'notes.txt' or 'src/main.py')
    """
    full_path = os.path.join(WORKSPACE_ROOT, path)
    if not os.path.exists(full_path):
        return f"Error: File not found: {full_path}"
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Write content to a file in the workspace. Creates parent directories if needed.

    Args:
        path: Relative path from workspace root
        content: File content to write
    """
    full_path = os.path.join(WORKSPACE_ROOT, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully wrote to {path}"


@mcp.tool()
def list_directory(path: str = ".") -> str:
    """List files and directories in the workspace.

    Args:
        path: Relative path from workspace root (default: '.')
    """
    full_path = os.path.join(WORKSPACE_ROOT, path)
    if not os.path.exists(full_path):
        return f"Error: Directory not found: {full_path}"
    entries = os.listdir(full_path)
    lines = []
    for entry in sorted(entries):
        full_entry = os.path.join(full_path, entry)
        prefix = "[DIR] " if os.path.isdir(full_entry) else "[FILE] "
        lines.append(prefix + entry)
    return "\n".join(lines) if lines else "Directory is empty"


@mcp.tool()
def append_file(path: str, content: str) -> str:
    """Append content to an existing file in the workspace.

    Args:
        path: Relative path from workspace root
        content: Content to append
    """
    full_path = os.path.join(WORKSPACE_ROOT, path)
    if not os.path.exists(full_path):
        return f"Error: File not found: {full_path}"
    with open(full_path, "a", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully appended to {path}"


if __name__ == "__main__":
    os.makedirs(WORKSPACE_ROOT, exist_ok=True)
    mcp.run(transport="stdio")
