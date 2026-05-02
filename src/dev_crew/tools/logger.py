"""Real-time logging for DevCrew agent execution.

Writes structured logs to both a log file and a callback that CrewAI
invokes on every agent step. Supports SSE push to browser clients.

The log file can be tailed with:
    tail -f logs/dev_crew.log
"""

import os
import time
import json
import threading
import asyncio
from collections import deque

_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "dev_crew.log")

_lock = threading.Lock()
_start_time = None

# --- SSE broadcast ---
_sse_queues: list[asyncio.Queue] = []
_sse_lock = threading.Lock()
# Keep recent events for late-joining clients
_event_history: deque = deque(maxlen=200)


def _broadcast(event: dict):
    """Push an event dict to all SSE subscriber queues."""
    with _sse_lock:
        _event_history.append(event)
        for q in _sse_queues:
            try:
                q.put_nowait(event)
            except Exception:
                pass


def subscribe() -> asyncio.Queue:
    """Create a new SSE subscriber queue. Call from async context."""
    q = asyncio.Queue()
    with _sse_lock:
        # Replay recent history
        for evt in _event_history:
            try:
                q.put_nowait(evt)
            except Exception:
                pass
        _sse_queues.append(q)
    return q


def unsubscribe(q: asyncio.Queue):
    """Remove an SSE subscriber queue."""
    with _sse_lock:
        if q in _sse_queues:
            _sse_queues.remove(q)


def _ensure_log_dir():
    os.makedirs(_LOG_DIR, exist_ok=True)


def _elapsed() -> str:
    if _start_time is None:
        return "0.0s"
    return f"{time.time() - _start_time:.1f}s"


def _elapsed_float() -> float:
    if _start_time is None:
        return 0.0
    return round(time.time() - _start_time, 1)


def log_event(source: str, message: str):
    """Append a timestamped log line. Thread-safe. Also broadcasts via SSE."""
    with _lock:
        _ensure_log_dir()
        ts = time.strftime("%H:%M:%S")
        elapsed = _elapsed()
        line = f"[{ts}] [{elapsed}] [{source}] {message}\n"
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
        print(line.rstrip(), flush=True)

    # Broadcast to SSE clients
    event = {
        "ts": ts,
        "elapsed": _elapsed_float(),
        "source": source,
        "message": message,
    }
    _broadcast(event)


def reset_timer():
    global _start_time
    _start_time = time.time()
    _ensure_log_dir()
    with open(_LOG_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== DevCrew Log Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
    # Clear SSE history
    with _sse_lock:
        _event_history.clear()


_cb_counter = 0


def make_step_callback(agent_name: str):
    """Create a step_callback for a CrewAI agent that logs every LLM step."""
    global _cb_counter
    _cb_counter += 1
    cb_id = _cb_counter
    # Strip whitespace/newlines from YAML folded block scalars
    _agent_names[cb_id] = agent_name.strip()

    def _callback(step):
        """Step callback for CrewAI agents (serializable)."""
        name = _agent_names.get(cb_id, "Agent")
        try:
            if hasattr(step, "text") and step.text:
                preview = step.text[:200].replace("\n", " ")
                log_event(name, f"LLM: {preview}...")
            elif hasattr(step, "tool") and step.tool:
                tool_input = str(getattr(step, "tool_input", ""))[:150]
                log_event(name, f"Tool call: {step.tool}({tool_input})")
            else:
                log_event(name, f"Step: {str(step)[:150]}")
        except Exception:
            pass

    return _callback


_agent_names: dict[int, str] = {}


def log_task_start(task_name: str, agent_name: str):
    log_event("CREW", f"Task started: {task_name} -> {agent_name}")


def log_task_done(task_name: str, agent_name: str, output_preview: str = ""):
    preview = output_preview[:100].replace("\n", " ") if output_preview else ""
    log_event("CREW", f"Task done: {task_name} ({agent_name}) {preview}...")


def log_crew_start(requirement: str):
    log_event("CREW", f"Crew started with requirement: {requirement[:100]}")


def log_crew_done():
    log_event("CREW", f"Crew completed. Total time: {_elapsed()}")
