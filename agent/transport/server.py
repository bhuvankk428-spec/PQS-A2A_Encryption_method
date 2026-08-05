import asyncio

from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration

from agent.transport.protocol import AgentProtocol

from agent.protocol.packet import Packet
from agent.protocol.constants import ACK


async def handle_stream(reader, writer):

    print("[SERVER] Stream Opened")

    while True:

        data = await reader.read(4096)

        if not data:
            break

        # Decode incoming packet
        packet = Packet.decode(data)

        print("\n========== PACKET RECEIVED ==========")
        print(f"Version     : {packet.version}")
        print(f"Type        : {packet.packet_type}")
        print(f"Session ID  : {packet.session_id}")
        print(f"Sequence    : {packet.sequence}")
        print(f"Payload     : {packet.payload.decode()}")
        print("====================================\n")

        # Build ACK packet
        ack_packet = Packet(
            packet_type=ACK,
            session_id=packet.session_id,
            sequence=packet.sequence + 1,
            payload=b"ACK",
        )

        # Send ACK
        writer.write(ack_packet.encode())

        await writer.drain()

    writer.close()

    print("[SERVER] Stream Closed")


def stream_handler(reader, writer):
    asyncio.create_task(handle_stream(reader, writer))


async def main():

    configuration = QuicConfiguration(
        is_client=False
    )

    configuration.load_cert_chain(
        "certs/cert.pem",
        "certs/key.pem",
    )

    await serve(
        host="0.0.0.0",
        port=4433,
        configuration=configuration,
        create_protocol=AgentProtocol,
        stream_handler=stream_handler,
    )

    print("Agent A Listening on UDP 4433")

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())