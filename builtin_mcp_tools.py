import io
import os.path
import subprocess
from datetime import datetime
from os import _Environ
from typing import Any, Optional, Union

import pyautogui
from PIL import Image
from RestrictedPython import compile_restricted, safe_globals
from mcp.server.fastmcp import FastMCP

mcp: FastMCP = FastMCP("builtin_mcp_tools", settings={"host": "0.0.0.0", "port": 8000})


@mcp.tool()
def execute_command(command: list[str], inputContent: Optional[str] = None) -> dict[str, Any]:
    """Execute the command in the shell."""
    result: subprocess.CompletedProcess = subprocess.run(command, input=inputContent, capture_output=True, text=True)
    return {"returnCode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


@mcp.tool()
def execute_python_code(code: str) -> dict[str, Any]:
    """Execute the python code in the shell."""
    byteCode = compile_restricted(code, "inline", "exec")
    localVars = {}
    exec(byteCode, safe_globals, localVars)
    return localVars


@mcp.tool()
def get_environment_variables() -> _Environ[str]:
    """Get the environment variables."""
    return os.environ


@mcp.tool()
def current_time() -> str:
    """Get the current time."""
    return "The current time is " + str(datetime.now())


@mcp.tool()
def create_directory(directory: str) -> Optional[Exception]:
    """Create a directory."""
    try:
        os.makedirs(directory)
        return None
    except Exception as e:
        return e


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
def delete_directory(directory: str) -> Optional[Exception]:
    """Delete a directory."""
    try:
        os.rmdir(directory)
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


@mcp.tool()
def exists(path: str) -> bool:
    """Check if a file or directory exists."""
    return os.path.exists(path)


@mcp.tool()
def is_file(path: str) -> bool:
    """Check if a file exists."""
    return os.path.isfile(path)


@mcp.tool()
def is_directory(filepath: str) -> bool:
    """Check if a directory exists."""
    return os.path.isdir(filepath)


@mcp.tool()
def list_directory(directory: str) -> list[str]:
    """List the contents of a directory."""
    return os.listdir(directory)


@mcp.tool()
def get_file_size(filepath: str) -> int:
    """Get the size of a file."""
    return os.path.getsize(filepath)


@mcp.tool()
def get_file_modified_time(filepath: str) -> str:
    """Get the modified time of a file."""
    return str(datetime.fromtimestamp(os.path.getmtime(filepath)))


@mcp.tool()
def get_file_created_time(filepath: str) -> str:
    """Get the created time of a file."""
    return str(datetime.fromtimestamp(os.path.getctime(filepath)))


@mcp.tool()
def get_file_accessed_time(filepath: str) -> str:
    """Get the accessed time of a file."""
    return str(datetime.fromtimestamp(os.path.getatime(filepath)))


@mcp.tool()
def screenshot_fullscreen() -> bytes:
    """Take a screenshot of the fullscreen."""
    image = pyautogui.screenshot()
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    binary_data = buffer.getvalue()
    buffer.close()
    return binary_data


@mcp.tool()
def screenshot_region(x: int, y: int, width: int, height: int) -> bytes:
    """Take a screenshot of a region."""
    image = pyautogui.screenshot(region=(x, y, width, height))
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    binary_data = buffer.getvalue()
    buffer.close()
    return binary_data


if __name__ == '__main__':
    mcp.run(transport="sse")
