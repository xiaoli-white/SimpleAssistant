import subprocess

from mcp.server.fastmcp import FastMCP

mcp: FastMCP = FastMCP("command-executor")


@mcp.tool()
def execute_command(command: list[str]) -> tuple[int, str, str]:
    """Execute the command in the shell."""
    result: subprocess.CompletedProcess = subprocess.run(command, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


if __name__ == '__main__':
    mcp.run(transport="sse")
