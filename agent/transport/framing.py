import struct

from agent.metrics import metrics

LENGTH_FORMAT = "!I"
LENGTH_SIZE = struct.calcsize(LENGTH_FORMAT)

# Upper bound for a single protocol packet. Defends against a hostile 32-bit
# length field causing an unbounded allocation (DoS).
MAX_PACKET_SIZE = 1 * 1024 * 1024


async def send_packet(writer, packet):

    data = packet.encode()

    header = struct.pack(
        LENGTH_FORMAT,
        len(data),
    )

    writer.write(header + data)

    # Metrics
    metrics.packet_sent(
        len(header) + len(data)
    )

    await writer.drain()


async def receive_packet(reader):

    header = await reader.readexactly(
        LENGTH_SIZE
    )

    packet_length = struct.unpack(
        LENGTH_FORMAT,
        header,
    )[0]

    if packet_length > MAX_PACKET_SIZE:
        raise ValueError(
            f"Packet length {packet_length} "
            f"exceeds maximum {MAX_PACKET_SIZE}"
        )

    packet = await reader.readexactly(
        packet_length
    )

    # Metrics
    metrics.packet_received(
        packet_length + LENGTH_SIZE
    )

    return packet