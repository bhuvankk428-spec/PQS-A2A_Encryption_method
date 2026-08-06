import struct

LENGTH_FORMAT = "!I"
LENGTH_SIZE = struct.calcsize(LENGTH_FORMAT)


async def send_packet(writer, packet):

    data = packet.encode()

    header = struct.pack(
        LENGTH_FORMAT,
        len(data),
    )

    writer.write(header + data)

    await writer.drain()


async def receive_packet(reader):

    # Read 4-byte packet length
    header = await reader.readexactly(
        LENGTH_SIZE
    )

    packet_length = struct.unpack(
        LENGTH_FORMAT,
        header,
    )[0]

    # Read exactly one complete packet
    packet = await reader.readexactly(
        packet_length
    )

    return packet