import asyncio
import ssl

from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

from agent.transport.protocol import AgentProtocol

from agent.session.manager import SessionManager
from agent.protocol.packet import Packet
from agent.protocol.engine import ProtocolEngine
from agent.protocol.state import SessionState
from agent.protocol.messages import MessageType

from agent.peer.peer import Peer
from agent.protocol.payloads.hello import HelloMessage

from agent.crypto.engine import CryptoEngine
from agent.transport.framing import (
    send_packet,
    receive_packet,
)

manager = SessionManager()


async def main():

    configuration = QuicConfiguration(
        is_client=True
    )
    
    configuration.verify_mode = ssl.CERT_NONE

    async with connect(
        "127.0.0.1",
        4433,
        configuration=configuration,
        create_protocol=AgentProtocol,
    ) as protocol:

        print("[CLIENT] Connected")

        reader, writer = await protocol.create_stream()

        # Create Session
        session = manager.create()

        session.set_state(SessionState.HELLO_SENT)

        # Create Peer
        peer = Peer.create("Agent-A")

        # Build HELLO
        hello = HelloMessage(
            peer.peer_id,
            peer.name,
            peer.version,
        )

        hello_packet = Packet(
            packet_type=MessageType.HELLO,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=hello.encode(),
        )

        await send_packet(
    writer,
    hello_packet,
)

        print("[CLIENT] HELLO Sent")

        # Prevent sending DATA multiple times
        data_sent = False

        while True:

            try:

                data = await receive_packet(
        reader,
    )

            except asyncio.IncompleteReadError:
                   break

            packet = Packet.decode(data)
            print("Packet Payload Length:", len(packet.payload))
            print(packet.payload)
            print(
                f"[CLIENT] Received Packet : {packet.packet_type}"
            )

            # -----------------------------
            # Encrypted DATA from server
            # -----------------------------
            if packet.packet_type == MessageType.DATA:

                plaintext = CryptoEngine.decrypt(
                    session,
                    packet.payload,
                )

                print()
                print("========== SERVER REPLY ==========")
                print(plaintext.decode())
                print("==================================")

                break

            # Let protocol process handshake packets
            response = ProtocolEngine.process(
                session,
                packet,
            )

            if response:
                await send_packet(writer,response,)

            # Send encrypted DATA once handshake completes
            if session.is_established() and not data_sent:

                print("[CLIENT] Secure Session Established")

                encrypted = CryptoEngine.encrypt(
                    session,
                    b"Hello Secure World"
                )

                secure_packet = Packet(
                    packet_type=MessageType.DATA,
                    session_id=session.session_id,
                    sequence=session.next_send_sequence(),
                    payload=encrypted,
                )

                print("[CLIENT] Sending DATA...")

                await send_packet(
    writer,
    secure_packet,
)

                print("[CLIENT] DATA flushed")

                await asyncio.sleep(5)

                print("[CLIENT] Encrypted DATA Sent")
                data_sent = True

# Keep connection alive so server can process DATA
                await asyncio.sleep(2)

        writer.close()
        await writer.wait_closed()

        print("[CLIENT] Connection Closed")

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())