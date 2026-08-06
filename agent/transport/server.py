import asyncio

from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration

from agent.transport.protocol import AgentProtocol
from agent.transport.framing import (
    send_packet,
    receive_packet,
)

from agent.session.manager import SessionManager
from agent.protocol.packet import Packet
from agent.protocol.engine import ProtocolEngine

manager = SessionManager()


async def handle_stream(reader, writer):

    print("[SERVER] Stream Opened")

    while True:

        try:

            # Read one complete framed packet
            print("[SERVER] Waiting for next packet...")
            data = await receive_packet(
                reader,
            )

        except asyncio.IncompleteReadError:
            break

        packet = Packet.decode(data)

        print("\n========== PACKET ==========")
        print("Type       :", packet.packet_type)
        print("Session ID :", packet.session_id)
        print("Sequence   :", packet.sequence)
        print("============================")

        # Find/Create Session
        session = manager.get_or_create(
            packet.session_id
        )

        # Let protocol handle it
        response = ProtocolEngine.process(
            session,
            packet,
        )

        # Send response if any
        if response:

            await send_packet(
                writer,
                response,
            )

    writer.close()

    await writer.wait_closed()

    print("[SERVER] Stream Closed")


def stream_handler(reader, writer):
    asyncio.create_task(
        handle_stream(reader, writer)
    )


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