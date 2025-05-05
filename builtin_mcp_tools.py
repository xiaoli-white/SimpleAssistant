import subprocess
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp: FastMCP = FastMCP("builtin_mcp_tools", settings={"host": "0.0.0.0", "port": 8000})


@mcp.tool()
def execute_command(command: list[str]) -> dict[str, Any]:
    """Execute the command in the shell."""
    result: subprocess.CompletedProcess = subprocess.run(command, capture_output=True, text=True)
    return {"returnCode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


if __name__ == '__main__':
    mcp.run(transport="sse")
