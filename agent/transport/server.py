import asyncio
import sys
from pathlib import Path

# Make the repo root importable when this script is run directly
# (``python agent/transport/server.py``). sys.path[0] would otherwise point
# at ``agent/transport`` and ``import agent`` would fail.
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
from agent.protocol.messages import MessageType
from monitor.server import start_monitor
from monitor.events import protocol_event

manager = SessionManager()


async def handle_stream(reader, writer):

    print("[SERVER] Stream Opened")

    metrics.connections += 1

    protocol_event(
        "CONNECT",
        "SERVER",
        "Agent B accepted a QUIC stream",
    )

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

    protocol_event(
        "DISCONNECT",
        "SERVER",
        "Agent B stream closed",
    )

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

    # --no-monitor: run purely as the QUIC peer. Used when the dashboard
    # monitor is already running standalone (monitor/server.py) and the
    # "Start Backend" button spawns this server as a subprocess.
    run_monitor = "--no-monitor" not in sys.argv

    if run_monitor:
        # Dashboard backend: serves the built React app + relays protocol events
        # to connected dashboards on http://localhost:5000.
        start_monitor(quic_server_active=True)

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