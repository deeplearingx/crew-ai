"""Web terminal multiplexer — tmux-style split-pane terminal in the browser.

Each browser pane creates a WebSocket connection with a unique session_id.
The server spawns a PTY process per session via pywinpty and bridges
stdin/stdout through the WebSocket.
"""

import os
import sys
import json
import asyncio
import threading
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="Terminal Multiplexer")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")


class TerminalSession:
    """Manages a single PTY process connected to a WebSocket via pywinpty."""

    def __init__(self, session_id: str, shell: str = "cmd.exe", cols: int = 80, rows: int = 24):
        self.session_id = session_id
        self.shell = shell
        self.pty = None
        self._running = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._ws: WebSocket | None = None
        self._output_queue: asyncio.Queue | None = None

    def start(self, ws: WebSocket, loop: asyncio.AbstractEventLoop, cols: int = 80, rows: int = 24):
        try:
            import winpty
            self.pty = winpty.PTY(cols, rows)
            self.pty.spawn(self.shell)
        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                ws.send_text(json.dumps({"type": "error", "data": f"Failed to start PTY: {e}"})),
                loop,
            )
            return False

        self._ws = ws
        self._loop = loop
        self._running = True
        self._output_queue = asyncio.Queue()

        t = threading.Thread(target=self._read_loop, daemon=True)
        t.start()
        return True

    def _read_loop(self):
        """Read PTY output in a background thread, push to asyncio queue."""
        import time
        try:
            while self._running and self.pty:
                try:
                    data = self.pty.read()
                    if data and self._loop and self._output_queue:
                        asyncio.run_coroutine_threadsafe(
                            self._output_queue.put(data), self._loop
                        )
                    else:
                        time.sleep(0.02)
                except OSError:
                    break
                except Exception:
                    time.sleep(0.05)
        finally:
            self._running = False
            if self._loop and self._output_queue:
                asyncio.run_coroutine_threadsafe(
                    self._output_queue.put(None), self._loop
                )

    async def read_output(self, ws: WebSocket):
        """Forward PTY output from queue to WebSocket."""
        try:
            while self._running or not self._output_queue.empty():
                try:
                    data = await asyncio.wait_for(self._output_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                if data is None:
                    break
                await ws.send_text(json.dumps({"type": "output", "data": data}))
        except (WebSocketDisconnect, ConnectionError, RuntimeError):
            pass
        finally:
            try:
                await ws.send_text(json.dumps({"type": "exit", "data": "Process exited"}))
            except Exception:
                pass

    def write_input(self, data: str):
        if self.pty:
            try:
                self.pty.write(data)
            except Exception:
                pass

    def resize(self, cols: int, rows: int):
        if self.pty:
            try:
                self.pty.set_size(cols, rows)
            except Exception:
                pass

    def kill(self):
        self._running = False
        if self.pty:
            try:
                del self.pty
            except Exception:
                pass
            self.pty = None


sessions: Dict[str, TerminalSession] = {}


@app.websocket("/ws/terminal")
async def ws_terminal(ws: WebSocket):
    await ws.accept()

    params = ws.query_params
    session_id = params.get("session_id", "")
    shell = params.get("shell", "cmd.exe")
    cols = int(params.get("cols", "80"))
    rows = int(params.get("rows", "24"))

    if not session_id:
        await ws.send_text(json.dumps({"type": "error", "data": "Missing session_id"}))
        await ws.close()
        return

    session = TerminalSession(session_id, shell, cols, rows)
    sessions[session_id] = session
    loop = asyncio.get_event_loop()
    ok = session.start(ws, loop, cols, rows)

    if not ok:
        sessions.pop(session_id, None)
        return

    async def listen_input():
        try:
            while True:
                raw = await ws.receive_text()
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                msg_type = msg.get("type")
                if msg_type == "input":
                    session.write_input(msg.get("data", ""))
                elif msg_type == "resize":
                    session.resize(msg.get("cols", 80), msg.get("rows", 24))
        except WebSocketDisconnect:
            pass

    try:
        await asyncio.gather(session.read_output(ws), listen_input())
    except Exception:
        pass
    finally:
        session.kill()
        sessions.pop(session_id, None)


@app.get("/")
def serve_terminal():
    return FileResponse(os.path.join(FRONTEND_DIR, "terminal.html"))


@app.get("/api/sessions")
def list_sessions():
    return {"sessions": list(sessions.keys())}


if __name__ == "__main__":
    import uvicorn
    print("Terminal Multiplexer starting on http://localhost:9001")
    uvicorn.run(app, host="0.0.0.0", port=9001)
