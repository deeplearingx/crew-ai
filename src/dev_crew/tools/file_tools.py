import os

from crewai.tools import tool
from dev_crew.tools.logger import log_event

_EXCLUDED_DIRS = {"venv", ".venv", "__pycache__", ".git", ".claude", "node_modules", ".idea", ".vscode"}


@tool("Read a file's content")
def read_file(file_path: str, start_line: int = 1, line_count: int | None = None) -> str:
    """Read the content of a file. Supports UTF-8 and GBK encoding on Windows."""
    log_event("TOOL", f"read_file({file_path})")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="gbk") as f:
                lines = f.readlines()
        except Exception as e:
            return f"Error reading {file_path}: {e}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error reading {file_path}: {e}"

    start = max(0, start_line - 1)
    end = start + line_count if line_count else len(lines)
    selected = lines[start:end]
    numbered = [f"{i + start + 1}: {line}" for i, line in enumerate(selected)]
    return "".join(numbered)


@tool("Write content to a file")
def write_file(path: str, content: str) -> str:
    """Write content to a file at the given path. Creates parent directories if needed."""
    log_event("TOOL", f"write_file({path}, {len(content)} chars)")
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing to {path}: {e}"


@tool("List files in a directory")
def list_directory(path: str) -> str:
    """List files and subdirectories in the given directory (non-recursive, excludes venv/git/etc)."""
    log_event("TOOL", f"list_directory({path})")
    try:
        entries = []
        for entry in sorted(os.listdir(path)):
            full = os.path.join(path, entry)
            if entry in _EXCLUDED_DIRS:
                continue
            if os.path.isdir(full):
                entries.append(f"[DIR]  {entry}/")
            else:
                entries.append(f"[FILE] {entry}")
        if not entries:
            return f"Directory '{path}' is empty (after filtering)."
        return "\n".join(entries)
    except FileNotFoundError:
        return f"Directory not found: {path}"
    except Exception as e:
        return f"Error listing {path}: {e}"
