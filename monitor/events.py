import json
import urllib.request

MONITOR_URL = "http://localhost:5000/api/emit"


def _relay_via_http(payload):
    try:
        request = urllib.request.Request(
            MONITOR_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        urllib.request.urlopen(
            request,
            timeout=1,
        )

    except Exception:
        # Monitor server not running: never crash
        # the protocol for a missing dashboard.
        pass


def protocol_event(
    event_type,
    source,
    message,
    **extra,
):
    payload = {
        "type": event_type,
        "source": source,
        "message": message,
        **extra,
    }

    # Events are emitted from agent processes while the
    # Socket.IO server lives inside the monitor process.
    # Relay over HTTP so events actually reach connected
    # dashboard clients. Synchronous + tiny timeout: a
    # localhost POST takes ~1ms and fails instantly if
    # the monitor is down.

    _relay_via_http(payload)
