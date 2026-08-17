"""Backend for the protocol dashboard.

Serves the built React dashboard (``dashboard/dist``) and exposes a
Socket.IO endpoint that streams live ``protocol_event`` messages emitted by
the agent.

The QUIC server process starts this monitor automatically
(``agent/transport/server.py``), so the dashboard can be opened at
``http://localhost:5000`` while a conversation runs. It can also be started
standalone: ``python monitor/server.py``.
"""
import subprocess
import sys
import threading
from pathlib import Path

# Make the repo root importable when this script is run directly.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, send_from_directory
from flask_socketio import SocketIO

from monitor import bridge

# SPA build output. Determined relative to the repo root (one level above
# this file).
DASHBOARD_DIST = ROOT / "dashboard" / "dist"

DASHBOARD_INDEX = DASHBOARD_DIST / "index.html"

app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
)

_client_process = None
_server_process = None

# Set to True by agent/transport/server.py before it starts the monitor, so
# handle_start_backend knows the QUIC server already lives in this process and
# must not spawn a duplicate one.
QUIC_SERVER_ACTIVE = False


def emit_log(event):
    socketio.emit(
        "protocol_event",
        event,
        namespace="/",
    )


def _relay_process_output(process, source):
    """Forward every line a subprocess prints to the dashboard.

    The QUIC client (and the QUIC server when spawned from here) run as
    separate processes, so besides the structured ``protocol_event`` messages
    they forward through :mod:`monitor.bridge`, their raw console output is
    streamed here as ``CONSOLE`` events. That way every step printed by the
    agents appears live in the dashboard.
    """
    for line in iter(process.stdout.readline, ""):
        line = line.rstrip("\r\n")
        if line:
            socketio.emit(
                "protocol_event",
                {
                    "type": "CONSOLE",
                    "source": source,
                    "message": line,
                },
                namespace="/",
            )


@socketio.on("protocol_event")
def handle_protocol_event(data):
    # The QUIC client runs as a separate subprocess and forwards its structured
    # events here through monitor.bridge (a Socket.IO client). Without this
    # rebroadcast those events would be dropped instead of reaching dashboards.
    socketio.emit(
        "protocol_event",
        data,
        namespace="/",
    )


@socketio.on("start_backend")
def handle_start_backend():
    global _client_process, _server_process

    # Both peers already running -> nothing to do.
    client_running = (
        _client_process is not None
        and _client_process.poll() is None
    )
    server_running = (
        _server_process is not None
        and _server_process.poll() is None
    )

    if client_running and (QUIC_SERVER_ACTIVE or server_running):
        socketio.emit(
            "backend_status",
            {"status": "already_running"},
            namespace="/",
        )
        return

    started = []

    # The QUIC server lives in this process only when agent/transport/server.py
    # started the monitor. Otherwise spawn it as a subprocess (without its own
    # monitor, which is already served from here).
    if not QUIC_SERVER_ACTIVE and not server_running:
        _server_process = subprocess.Popen(
            [
                sys.executable,
                str(ROOT / "agent" / "transport" / "server.py"),
                "--no-monitor",
            ],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        threading.Thread(
            target=_relay_process_output,
            args=(_server_process, "SERVER"),
            daemon=True,
        ).start()
        started.append("server")

    client_script = ROOT / "agent" / "transport" / "client.py"

    _client_process = subprocess.Popen(
        [sys.executable, str(client_script)],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    threading.Thread(
        target=_relay_process_output,
        args=(_client_process, "CLIENT"),
        daemon=True,
    ).start()
    started.append("client")

    socketio.emit(
        "backend_status",
        {"status": "started", "components": started},
        namespace="/",
    )

    def _wait_and_notify():
        _client_process.wait()
        socketio.emit(
            "backend_status",
            {"status": "finished"},
            namespace="/",
        )

    threading.Thread(
        target=_wait_and_notify,
        daemon=True,
    ).start()


def _serve_index():
    if DASHBOARD_INDEX.is_file():
        return send_from_directory(
            str(DASHBOARD_DIST),
            "index.html",
        )
    return (
        "Quantum Secure Monitor Running. "
        "Build the dashboard first with "
        "`npm --prefix dashboard run build`."
    )


@app.route("/")
def home():
    return _serve_index()


@app.route("/<path:path>")
def static_files(path):
    asset = (DASHBOARD_DIST / path).resolve()

    dashboard_root = DASHBOARD_DIST.resolve()

    # Only serve files that are actually inside the dist folder.
    if (
        str(asset).startswith(str(dashboard_root))
        and asset.is_file()
    ):
        return send_from_directory(
            str(DASHBOARD_DIST),
            path,
        )

    # SPA fallback: unknown routes return the dashboard entry point.
    return _serve_index()


def run_monitor(host="0.0.0.0", port=5000):
    bridge.attach(socketio)
    socketio.run(
        app,
        host=host,
        port=port,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
        log_output=False,
    )


def start_monitor(host="0.0.0.0", port=5000, quic_server_active=False):
    """Start the dashboard/socket server in a background thread.

    Used by the QUIC server process so protocol events emitted from the same
    process can be streamed to connected dashboards.

    ``quic_server_active`` tells :func:`handle_start_backend` that the QUIC
    server already runs in this process, so clicking "Start Backend" only has
    to spawn the client.
    """
    global QUIC_SERVER_ACTIVE
    QUIC_SERVER_ACTIVE = quic_server_active

    thread = threading.Thread(
        target=run_monitor,
        args=(host, port),
        daemon=True,
    )
    thread.start()
    return thread


if __name__ == "__main__":
    run_monitor()