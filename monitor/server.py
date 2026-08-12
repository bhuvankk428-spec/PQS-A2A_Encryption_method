"""Backend for the protocol dashboard.

Serves the built React dashboard (``dashboard/dist``) and exposes a
Socket.IO endpoint that streams live ``protocol_event`` messages emitted by
the agent.

The QUIC server process starts this monitor automatically
(``agent/transport/server.py``), so the dashboard can be opened at
``http://localhost:5000`` while a conversation runs. It can also be started
standalone: ``python monitor/server.py``.
"""
import threading
from pathlib import Path

from flask import Flask, send_from_directory
from flask_socketio import SocketIO

# SPA build output. Determined relative to the repo root (one level above
# this file).
DASHBOARD_DIST = (
    Path(__file__).resolve().parent.parent
    / "dashboard"
    / "dist"
)

DASHBOARD_INDEX = DASHBOARD_DIST / "index.html"

app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
)


def emit_log(event):
    socketio.emit(
        "protocol_event",
        event,
        namespace="/",
    )


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
    socketio.run(
        app,
        host=host,
        port=port,
        debug=False,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
        log_output=False,
    )


def start_monitor(host="0.0.0.0", port=5000):
    """Start the dashboard/socket server in a background thread.

    Used by the QUIC server process so protocol events emitted from the same
    process can be streamed to connected dashboards.
    """
    thread = threading.Thread(
        target=run_monitor,
        args=(host, port),
        daemon=True,
    )
    thread.start()
    return thread


if __name__ == "__main__":
    run_monitor()