import struct

from agent.metrics import metrics

LENGTH_FORMAT = "!I"
LENGTH_SIZE = struct.calcsize(LENGTH_FORMAT)


async def send_packet(writer, packet):

    data = packet.encode()

    header = struct.pack(
        LENGTH_FORMAT,
        len(data),
    )

    writer.write(header + data)

    # Metrics
    metrics.packet_sent(
        len(header + data)
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

    packet = await reader.readexactly(
        packet_length
    )

    # Metrics
    metrics.packet_received(
        packet_length + LENGTH_SIZE
    )

    return packet