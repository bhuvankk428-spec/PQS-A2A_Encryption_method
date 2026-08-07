import asyncio
import contextlib
import ssl

from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

from agent.crypto.engine import CryptoEngine
from agent.metrics import metrics
from agent.peer.peer import Peer
from agent.protocol.engine import ProtocolEngine
from agent.protocol.messages import MessageType
from agent.protocol.packet import Packet
from agent.protocol.payloads.hello import HelloMessage
from agent.protocol.payloads.ping import PingMessage
from agent.protocol.payloads.rehandshake import ReHandshakeMessage
from agent.protocol.payloads.resume import ResumeMessage
from agent.protocol.state import SessionState
from agent.security.forward_secrecy import ForwardSecrecy
from agent.session.cache import SessionCache
from agent.session.manager import SessionManager
from agent.transport.framing import receive_packet, send_packet
from agent.transport.protocol import AgentProtocol

manager = SessionManager()


async def heartbeat(session, writer):
    while session.is_established():
        await asyncio.sleep(5)

        ping = PingMessage()

        packet = Packet(
            packet_type=MessageType.PING,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=ping.encode(),
        )

        await send_packet(
            writer,
            packet,
        )

        print("[CLIENT] PING Sent")


async def main():
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = ssl.CERT_NONE

    async with connect(
        "127.0.0.1",
        4433,
        configuration=configuration,
        create_protocol=AgentProtocol,
    ) as protocol:
        print("[CLIENT] Connected")
        metrics.connections += 1

        reader, writer = await protocol.create_stream()

        # Session creation with cache check
        session = manager.create()
        cache = SessionCache.load()
        resume_mode = cache is not None

        peer = Peer.create("Agent-A")

        if resume_mode:
            print("[CLIENT] Cached session found")
        else:
            print("[CLIENT] No cached session")

        session.set_state(SessionState.HELLO_SENT)

        # Conditional HELLO vs RESUME packet creation
        if resume_mode:
            resume = ResumeMessage(cache["session_id"])

            packet = Packet(
                packet_type=MessageType.RESUME,
                session_id=session.session_id,
                sequence=session.next_send_sequence(),
                payload=resume.encode(),
            )

            print("[CLIENT] RESUME Sent")
        else:
            metrics.start_handshake()

            hello = HelloMessage(
                peer.peer_id,
                peer.name,
                peer.version,
            )

            packet = Packet(
                packet_type=MessageType.HELLO,
                session_id=session.session_id,
                sequence=session.next_send_sequence(),
                payload=hello.encode(),
            )

            print("[CLIENT] HELLO Sent")

        await send_packet(
            writer,
            packet,
        )

        data_sent = False
        heartbeat_task = None
        handshake_completed = False

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
            print(f"[CLIENT] Received Packet : {packet.packet_type}")

            # -----------------------------
            # Handle RESUME Response
            # -----------------------------
            if packet.packet_type == MessageType.RESUME:
                print()
                print("========== SESSION RESUME ==========")
                print("Secure session resumed")
                print("====================================")

                session.crypto.load_shared_secret(
                    cache["shared_secret"],
                    is_client=True,
                )

                session.crypto.key_version = cache["key_version"]
                session.crypto.establish()
                session.set_state(SessionState.ESTABLISHED)

                metrics.resume_successful()

            # -----------------------------
            # Encrypted DATA Handling
            # -----------------------------
            elif packet.packet_type == MessageType.DATA:
                plaintext = CryptoEngine.decrypt(
                    session,
                    packet.payload,
                )

                print()
                print("========== SERVER REPLY ==========")
                print(plaintext.decode())
                print("==================================")

                # Do not terminate the connection while a re-handshake is in progress
                if session.rehandshaking:
                    print("[CLIENT] Waiting for new Kyber handshake...")
                    continue

                print("[CLIENT] Conversation Finished")
                break

            else:
                # Let protocol process handshake packets (KYBER_PUBLIC_KEY, KEY_CONFIRM, etc.)
                response = ProtocolEngine.process(
                    session,
                    packet,
                )

                if response:
                    await send_packet(
                        writer,
                        response,
                    )

            # Record full handshake metrics when establishing a new session
            if (
                session.is_established()
                and not resume_mode
                and not handshake_completed
            ):
                metrics.handshakes += 1
                metrics.finish_handshake()
                handshake_completed = True

            # -----------------------------
            # Post-Rehandshake Verification Transmit
            # -----------------------------
            if getattr(session, "send_after_rehandshake", False):
                encrypted = CryptoEngine.encrypt(
                    session,
                    b"Forward Secrecy Verified",
                )

                secure_packet = Packet(
                    packet_type=MessageType.DATA,
                    session_id=session.session_id,
                    sequence=session.next_send_sequence(),
                    payload=encrypted,
                )

                await send_packet(writer, secure_packet)

                print("[CLIENT] DATA sent with fresh keys")

                metrics.rekeys += 1
                session.send_after_rehandshake = False

            # -----------------------------
            # Initial Encrypted DATA Transmit
            # -----------------------------
            if session.is_established() and not data_sent:
                print("[CLIENT] Secure Session Established")

                heartbeat_task = asyncio.create_task(
                    heartbeat(
                        session,
                        writer,
                    )
                )
                print("[CLIENT] Sending DATA...")

                encrypted = CryptoEngine.encrypt(
                    session,
                    b"Hello Secure World",
                )

                secure_packet = Packet(
                    packet_type=MessageType.DATA,
                    session_id=session.session_id,
                    sequence=session.next_send_sequence(),
                    payload=encrypted,
                )

                await send_packet(
                    writer,
                    secure_packet,
                )

                print("[CLIENT] DATA flushed")

                print("Messages Sent :", session.crypto.messages_sent)
                print("Should ReHandshake :", ForwardSecrecy.should_rehandshake(session))

                if ForwardSecrecy.should_rehandshake(session):
                    print("[CLIENT] Requesting Full Re-Handshake")

                    session.rehandshaking = True
                    session.set_state(SessionState.HELLO_SENT)

                    rehandshake = ReHandshakeMessage()

                    rehandshake_packet = Packet(
                        packet_type=MessageType.REHANDSHAKE,
                        session_id=session.session_id,
                        sequence=session.next_send_sequence(),
                        payload=rehandshake.encode(),
                    )

                    await send_packet(
                        writer,
                        rehandshake_packet,
                    )

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

                    data_sent = True
                    continue

                await asyncio.sleep(5)

                print("[CLIENT] Encrypted DATA Sent")
                data_sent = True

                await asyncio.sleep(2)

        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await heartbeat_task

        writer.close()

        try:
            await writer.wait_closed()
        except asyncio.CancelledError:
            pass

        print("[CLIENT] Connection Closed")
        print()
        metrics.print()

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())