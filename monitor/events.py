from monitor import bridge


def protocol_event(
    event_type,
    source,
    message,
    **extra,
):
    bridge.emit_event({
        "type": event_type,
        "source": source,
        "message": message,
        **extra,
    })