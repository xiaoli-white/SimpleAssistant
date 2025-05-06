import os.path
import subprocess
from datetime import datetime
from typing import Any, Optional, Union

from mcp.server.fastmcp import FastMCP

mcp: FastMCP = FastMCP("builtin_mcp_tools", settings={"host": "0.0.0.0", "port": 8000})


@mcp.tool()
def execute_command(command: list[str]) -> dict[str, Any]:
    """Execute the command in the shell."""
    result: subprocess.CompletedProcess = subprocess.run(command, capture_output=True, text=True)
    return {"returnCode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


@mcp.tool()
def current_time() -> str:
    """Get the current time."""
    return "The current time is " + str(datetime.now())


@mcp.tool()
def create_file(filepath: str) -> Optional[Exception]:
    """Create a file."""
    if os.path.exists(filepath):
        return None
    try:
        with open(filepath, "w") as f:
            pass
        return None
    except Exception as e:
        return e


@mcp.tool()
def read_file(filepath: str, encoding: str = "utf-8", isBinary: bool = False) -> Union[str, Exception]:
    """Read a file."""
    try:
        with open(filepath, "rb" if isBinary else "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        return e


@mcp.tool()
def write_file(filepath: str, content: str, encoding: str = "utf-8", isBinary: bool = False) -> Optional[Exception]:
    """Write a file."""
    try:
        with open(filepath, "wb" if isBinary else "w", encoding=encoding) as f:
            f.write(content)
        return None
    except Exception as e:
        return e


@mcp.tool()
def delete_file(filepath: str) -> Optional[Exception]:
    """Delete a file."""
    try:
        os.remove(filepath)
        return None
    except Exception as e:
        return e


if __name__ == '__main__':
    mcp.run(transport="sse")
