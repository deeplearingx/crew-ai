import subprocess

from crewai.tools import tool
from dev_crew.tools.logger import log_event


@tool("Execute a shell command")
def run_command(command: str, timeout: int = 120) -> str:
    """Execute a shell command and return its stdout and stderr. Timeout in seconds (default 120)."""
    log_event("TOOL", f"run_command({command[:100]})")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        output += f"Return code: {result.returncode}"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {e}"
