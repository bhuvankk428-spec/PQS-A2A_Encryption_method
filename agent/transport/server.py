import asyncio

from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration

from agent.transport.protocol import AgentProtocol
from agent.transport.framing import (
    send_packet,
    receive_packet,
)
from agent.metrics import metrics
from agent.session.manager import SessionManager
from agent.protocol.packet import Packet
from agent.protocol.engine import ProtocolEngine
from monitor.server import start_monitor

manager = SessionManager()


async def handle_stream(reader, writer):

    print("[SERVER] Stream Opened")

    metrics.connections += 1

    while True:

        try:
            print("[SERVER] Waiting for next packet...")

            data = await receive_packet(
                reader,
            )

        except asyncio.IncompleteReadError:
            break

        try:
            packet = Packet.decode(data)
        except ValueError as exc:
            print(f"[SERVER] Malformed packet rejected: {exc}")
            continue

        print("\n========== PACKET ==========")
        print("Type       :", packet.packet_type)
        print("Session ID :", packet.session_id)
        print("Sequence   :", packet.sequence)
        print("============================")

        # Find/Create Session
        session = manager.get_or_create(
            packet.session_id
        )

        # -----------------------------
        # Replay Protection
        # -----------------------------
        if not session.replay.validate(
            packet.sequence
        ):

            metrics.replay_attack()

            print(
                f"[SECURITY] Replay attack detected "
                f"(Sequence={packet.sequence})"
            )

            continue

        # Update receive sequence
        session.update_receive_sequence(
            packet.sequence
        )

        # Let protocol handle packet
        response = ProtocolEngine.process(
            session,
            packet,
        )

        # Send response if protocol generated one
        if response:
            await send_packet(
                writer,
                response,
            )

    writer.close()

    # NOTE: writer.wait_closed() only resolves once the QUIC connection closes,
    # so we let the connection teardown handle it instead.
    print("[SERVER] Stream Closed")

    print()
    metrics.print()


def stream_handler(reader, writer):
    asyncio.create_task(
        handle_stream(
            reader,
            writer,
        )
    )


async def main():

    # Dashboard backend: serves the built React app + relays protocol events
    # to connected dashboards on http://localhost:5000.
    start_monitor()

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