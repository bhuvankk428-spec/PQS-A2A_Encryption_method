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
from agent.protocol.payloads.rekey import RekeyMessage
from agent.protocol.payloads.resume import ResumeMessage
from agent.protocol.state import SessionState
from agent.security.forward_secrecy import ForwardSecrecy
from agent.security.rotation import KeyRotation
from agent.session.cache import SessionCache
from agent.session.manager import SessionManager
from agent.transport.framing import receive_packet, send_packet
from agent.transport.protocol import AgentProtocol
from agent.ai.model import AIModel

agent_a = AIModel("Agent A")
manager = SessionManager()


async def send_rekey(session, writer):
    # Initiator rotates before sending REKEY. The REKEY packet
    # travels on the same ordered stream, so the peer receives it
    # before the next encrypted DATA packet.
    version = KeyRotation.next_version(session)

    session.rekey_pending = True

    KeyRotation.rotate(
        session,
        version=version,
    )

    packet = Packet(
        packet_type=MessageType.REKEY,
        session_id=session.session_id,
        sequence=session.next_send_sequence(),
        payload=RekeyMessage(version).encode(),
    )

    await send_packet(
        writer,
        packet,
    )

    print(f"[CLIENT] Mini session rotated -> v{version}")


async def request_rehandshake(session, writer, peer):
    print("[CLIENT] Requesting Full Re-Handshake")

    session.rehandshaking = True
    session.awaiting_reply = False
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


async def maybe_rotate(session, writer, peer):
    if (
        not session.is_established()
        or session.rehandshaking
        or session.rekey_pending
        or session.awaiting_reply
    ):
        return

    # Major key: one full ML-KEM handshake per hour
    if ForwardSecrecy.should_rehandshake(session):
        await request_rehandshake(
            session,
            writer,
            peer,
        )

        return

    # Mini key: every 6 minutes or 10 encrypted messages
    if KeyRotation.should_rotate(session):
        await send_rekey(
            session,
            writer,
        )


async def heartbeat(session, writer, peer):
    while session.is_established():
        await asyncio.sleep(5)

        if session.rehandshaking:
            break

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

        await maybe_rotate(
            session,
            writer,
            peer,
        )


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
        awaiting_resume_ack = resume_mode

        message_count = 0

        while True:
            try:
                if awaiting_resume_ack:
                    data = await asyncio.wait_for(
                        receive_packet(reader),
                        timeout=10,
                    )
                else:
                    data = await receive_packet(
                        reader,
                    )
            except asyncio.TimeoutError:
                # The server did not answer RESUME (for example an
                # older server process). Fall back to a full handshake
                # instead of blocking forever.
                print()
                print("========== SESSION RESUME ==========")
                print("Resume timed out; starting full handshake")
                print("====================================")

                SessionCache.clear()
                resume_mode = False
                awaiting_resume_ack = False
                metrics.start_handshake()

                # REHANDSHAKE makes the server accept HELLO even if it
                # already resumed the old ticket in the meantime.
                await request_rehandshake(
                    session,
                    writer,
                    peer,
                )

                continue
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
                resume = ResumeMessage.decode(packet.payload)
                awaiting_resume_ack = False

                # We already gave up on RESUME and started a fresh
                # handshake. A late ACK must not override that state.
                if session.rehandshaking:
                    print(
                        "[CLIENT] Ignoring late RESUME response "
                        "(re-handshake in progress)"
                    )
                    continue

                if not resume.success:
                    print()
                    print("========== SESSION RESUME ==========")
                    print("Resume rejected; starting full handshake")
                    print("====================================")

                    SessionCache.clear()
                    resume_mode = False
                    metrics.start_handshake()

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
                    continue

                print()
                print("========== SESSION RESUME ==========")
                print("Secure session resumed")
                print("====================================")

                session.crypto.key_version = cache["key_version"]

                session.crypto.load_shared_secret(
                    cache["shared_secret"],
                    is_client=True,
                )

                session.major_established_at = cache.get(
                    "created_at",
                    session.major_established_at,
                )
                session.crypto.key_rotated_at = (
                    session.major_established_at
                )

                session.crypto.establish()
                session.set_state(SessionState.ESTABLISHED)

                metrics.resume_successful()

            # -----------------------------
            # Encrypted DATA Handling
            # -----------------------------
            elif packet.packet_type == MessageType.DATA:

                try:
                    plaintext = CryptoEngine.decrypt(
                        session,
                        packet.payload,
                    )

                except Exception as e:

                    print()
                    print("========== PROTOCOL ERROR ==========")
                    print("Unable to decrypt reply:", type(e).__name__)
                    print("Attempting a fresh handshake")
                    print("====================================")

                    if not session.rehandshaking:
                        await request_rehandshake(
                            session,
                            writer,
                            peer,
                        )

                    continue

                session.awaiting_reply = False

                print()
                print("========== Agent B ==========")
                print(plaintext.decode())
                print("=============================")

                # Rotate at a safe point: no reply is in flight
                await maybe_rotate(
                    session,
                    writer,
                    peer,
                )

                if session.rehandshaking:
                    print("[CLIENT] Waiting for new Kyber handshake...")
                    continue

                from agent.ai.model import AIModel

                reply = agent_a.chat(
                    f"""
                You are Agent A.

                You are communicating with Agent B through a secure quantum-encrypted protocol.

                Your reply must:
                - be ONE sentence only
                - be under 15 words
                - never use markdown
                - never use bullet points
                - never say "I didn't understand"
                - continue the conversation naturally

                Agent B said:
                {plaintext.decode()}
                """
                )
                print()
                print("========== Agent A ==========")
                print(reply)
                print("=============================")
                await asyncio.sleep(3)

                if session.rehandshaking:
                    print("[CLIENT] Waiting for new Kyber handshake...")
                    continue

                session.awaiting_reply = True

                encrypted = CryptoEngine.encrypt(
                    session,
                    reply.encode(),
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

                message_count += 1

                print(f"[CLIENT] Messages Exchanged: {message_count}")
                continue

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

                if getattr(session, "error_received", False):
                    session.error_received = False

                    print()
                    print("========== PROTOCOL ERROR ==========")
                    print("Peer reported a secure-data error")
                    print("Attempting a fresh handshake")
                    print("====================================")

                    if not session.rehandshaking:
                        await request_rehandshake(
                            session,
                            writer,
                            peer,
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
                session.awaiting_reply = True

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

                # Heartbeat stops while the session leaves ESTABLISHED
                if heartbeat_task is None or heartbeat_task.done():
                    heartbeat_task = asyncio.create_task(
                        heartbeat(
                            session,
                            writer,
                            peer,
                        )
                    )

            # -----------------------------
            # Initial Encrypted DATA Transmit
            # -----------------------------
            if session.is_established() and not data_sent:
                print("[CLIENT] Secure Session Established")

                heartbeat_task = asyncio.create_task(
                    heartbeat(
                        session,
                        writer,
                        peer,
                    )
                )
                print("[CLIENT] Sending DATA...")

                reply = agent_a.chat(
                    "Say hello to another AI agent in one short sentence.")

                print()
                print("Agent A:", reply)
                print()

                session.awaiting_reply = True

                encrypted = CryptoEngine.encrypt(
                    session,
                    reply.encode(),
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
                message_count += 1
                print("[CLIENT] DATA flushed")

                print("Messages Sent :", session.crypto.messages_sent)

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