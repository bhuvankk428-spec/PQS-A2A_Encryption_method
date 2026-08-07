from monitor.server import emit_log


def protocol_event(
    event_type,
    source,
    message,
    **extra,
):
    emit_log({
        "type": event_type,
        "source": source,
        "message": message,
        **extra,
    })