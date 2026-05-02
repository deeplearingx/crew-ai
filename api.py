"""FastAPI backend: Calculator API + DevCrew visualization dashboard."""

import sys
import os
import re
import json
import asyncio

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from calculator.core import calculate
from calculator.validator import validate_number, validate_operator

app = FastAPI(title="DevCrew")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_LOG_FILE = os.path.join(os.path.dirname(__file__), "logs", "dev_crew.log")

_LOG_RE = re.compile(
    r"\[(\d{2}:\d{2}:\d{2})\]\s+\[([^\]]+?)\]\s+\[([^\]]+?)\]\s+(.*?)(?=\n\[|\Z)",
    re.DOTALL,
)


def _parse_log_lines(text: str) -> list[dict]:
    events = []
    for m in _LOG_RE.finditer(text):
        events.append({
            "ts": m.group(1),
            "elapsed": m.group(2),
            "source": m.group(3).strip(),
            "message": m.group(4).strip(),
        })
    return events


def _read_log_lines() -> list[str]:
    """Read all lines from the log file safely."""
    try:
        if os.path.exists(_LOG_FILE):
            with open(_LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
                return f.readlines()
    except Exception:
        pass
    return []


# --- Calculator API ---

class CalcRequest(BaseModel):
    a: float
    operator: str
    b: float


class CalcResponse(BaseModel):
    result: float
    expression: str


@app.post("/api/calculate", response_model=CalcResponse)
def api_calculate(req: CalcRequest):
    try:
        validate_number(str(req.a))
        validate_operator(req.operator)
        validate_number(str(req.b))
        result = calculate(req.a, req.operator, req.b)
        return CalcResponse(result=result, expression=f"{req.a} {req.operator} {req.b} = {result}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- SSE stream via log file tail (line-based) ---

# Track offset as line number (not bytes) to avoid encoding issues on Windows
_sse_offsets: dict[str, int] = {}


@app.get("/api/events")
async def sse_events(request: Request):
    """Server-Sent Events endpoint that tails the DevCrew log file."""

    # Start from current end of file (skip history — /api/history handles that)
    initial_lines = _read_log_lines()
    line_offset = len(initial_lines)

    async def stream():
        nonlocal line_offset
        try:
            while True:
                if await request.is_disconnected():
                    break

                new_events = []
                try:
                    all_lines = _read_log_lines()
                    if len(all_lines) > line_offset:
                        new_content = "".join(all_lines[line_offset:])
                        line_offset = len(all_lines)
                        new_events = _parse_log_lines(new_content)
                except Exception:
                    pass

                for evt in new_events:
                    yield f"data: {json.dumps(evt, ensure_ascii=False)}\n\n"

                if not new_events:
                    yield ": heartbeat\n\n"
                    await asyncio.sleep(0.5)
                else:
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass

    return StreamingResponse(stream(), media_type="text/event-stream")


# --- Replay existing log history ---

@app.get("/api/history")
def sse_history():
    """Return all existing log events as JSON."""
    lines = _read_log_lines()
    return _parse_log_lines("".join(lines))


# --- Static pages ---

@app.get("/")
def serve_dashboard():
    return FileResponse(os.path.join(os.path.dirname(__file__), "frontend", "dashboard.html"))


@app.get("/calc")
def serve_calculator():
    return FileResponse(os.path.join(os.path.dirname(__file__), "frontend", "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
