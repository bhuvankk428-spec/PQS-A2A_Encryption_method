"""Bridge that streams protocol events to the dashboard from any process.

The QUIC *server* process hosts the monitor backend (Flask-SocketIO) in the
same process, so events emitted there are pushed straight to connected
dashboards through the running Socket.IO server instance.

The QUIC *client* runs as a separate subprocess (started from the dashboard).
Events emitted in that process cannot use the in-process server, so a
lightweight Socket.IO *client* connects to the monitor backend on
localhost:5000 and forwards events over the network.

Events emitted before the Socket.IO client has connected are queued and
flushed as soon as the connection is established, so no step is ever lost.
"""
import queue
import threading
import time

_IN_PROCESS = None  # the live Socket.IO server instance (server process)
_client = None  # socketio.Client() (client subprocess)
_connecting = False
_pending = queue.Queue()
_lock = threading.Lock()

# How many times to retry connecting to the monitor before giving up. The
# client is often started before (or as) the monitor comes up, so a bounded
# retry with a short backoff keeps events flowing instead of dropping them.
_MAX_ATTEMPTS = 30
_RETRY_DELAY = 2.0


def attach(socketio):
    """Register the in-process Socket.IO server.

    Called by ``monitor.server`` right before it starts serving, so events
    emitted by the same process are delivered directly to dashboards.
    """
    global _IN_PROCESS
    _IN_PROCESS = socketio


def start(url="http://localhost:5000"):
    """Connect to the monitor backend from a background thread.

    Used by the QUIC client subprocess so its protocol events reach the
    dashboard. Events emitted before the connection is ready are buffered and
    flushed as soon as it succeeds.
    """
    global _connecting
    with _lock:
        if _client is not None or _connecting:
            return
        _connecting = True

    threading.Thread(
        target=_connect,
        args=(url,),
        daemon=True,
    ).start()


def _connect(url):
    global _client, _connecting
    client = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            import socketio

            candidate = socketio.Client(reconnection=True)
            candidate.connect(url, transports=["websocket"])
            client = candidate
            break
        except Exception as exc:  # pragma: no cover - depends on external backend
            print(
                f"[MONITOR] Bridge connection failed "
                f"(attempt {attempt}/{_MAX_ATTEMPTS}): {exc}"
            )
            time.sleep(_RETRY_DELAY)

    if client is None:
        print("[MONITOR] Bridge connection gave up; events remain buffered")
        with _lock:
            _connecting = False
        return

    with _lock:
        _client = client
        _connecting = False

        while not _pending.empty():
            try:
                item = _pending.get_nowait()
            except queue.Empty:
                break
            client.emit("protocol_event", item, namespace="/")


def emit_event(payload):
    """Send a protocol event to the dashboard from whichever process we are in."""
    if _IN_PROCESS is not None:
        _IN_PROCESS.emit("protocol_event", payload, namespace="/")
        return

    with _lock:
        if _client is not None and _client.connected:
            _client.emit("protocol_event", payload, namespace="/")
            return

        _pending.put(payload)