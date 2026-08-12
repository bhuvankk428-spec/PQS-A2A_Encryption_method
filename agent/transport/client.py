import asyncio
import contextlib
import secrets
import ssl
import time

from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

from agent.crypto.engine import CryptoEngine
from agent.metrics import metrics
from agent.peer.peer import Peer
from agent.protocol.engine import ProtocolEngine
from agent.protocol.messages import MessageType
from agent.protocol.packet import Packet
from agent.protocol.payloads.hello import HelloMessage
from agent.protocol.payloads.error import ErrorMessage
from agent.protocol.payloads.ping import PingMessage
from agent.protocol.payloads.rehandshake import ReHandshakeMessage
from agent.protocol.payloads.resume import ResumeMessage
from agent.protocol.state import SessionState
from agent.security.forward_secrecy import ForwardSecrecy
from agent.session.cache import SessionCache
from agent.session.manager import SessionManager
from agent.transport.framing import receive_packet, send_packet
from agent.transport.protocol import AgentProtocol
from agent.ai.model import AIModel

agent_a = AIModel("Agent A")
manager = SessionManager()

MAX_MESSAGES = 8


async def heartbeat(session, writer):
    while session.active:
        await asyncio.sleep(5)

        if not session.is_established():
            continue

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


async def send_hello(writer, session, peer):
    session.set_state(SessionState.HELLO_SENT)
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

    await send_packet(writer, packet)

    print("[CLIENT] HELLO Sent")


async def request_keypair_rotation(writer, session, peer):
    """Trigger a full ML-KEM key-pair rotation (fresh Kyber handshake).

    This discards the old shared secret and installs fresh AES keys, keeping
    the session resistant to long-term kyber key-pair exposure and
    side-channel leakage (post-quantum forward secrecy).
    """
    print("[CLIENT] Requesting FRESH Kyber key-pair rotation")

    session.rehandshaking = True
    session.last_rehandshake = time.time()
    session.set_state(SessionState.HELLO_SENT)

    rehandshake = ReHandshakeMessage()

    rehandshake_packet = Packet(
        packet_type=MessageType.REHANDSHAKE,
        session_id=session.session_id,
        sequence=session.next_send_sequence(),
        payload=rehandshake.encode(),
    )

    await send_packet(writer, rehandshake_packet)

    await send_hello(writer, session, peer)


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
        resume_salt = None

        peer = Peer.create("Agent-A")

        if resume_mode:
            print("[CLIENT] Cached session found")

            # Fresh random salt -> fresh AES keys on this connection, so the
            # (key, nonce) pairs of the previous connection are never reused.
            resume_salt = secrets.token_hex(16)

            resume = ResumeMessage(
                cache["session_id"],
                resume_salt,
            )

            packet = Packet(
                packet_type=MessageType.RESUME,
                session_id=session.session_id,
                sequence=session.next_send_sequence(),
                payload=resume.encode(),
            )

            print("[CLIENT] RESUME Sent")

            await send_packet(
                writer,
                packet,
            )
        else:
            print("[CLIENT] No cached session")
            await send_hello(writer, session, peer)

        data_sent = False
        heartbeat_task = None
        message_count = 0

        while message_count < MAX_MESSAGES:
            try:
                data = await receive_packet(
                    reader,
                )
            except asyncio.IncompleteReadError:
                break

            try:
                packet = Packet.decode(data)
            except ValueError as exc:
                print(f"[CLIENT] Malformed packet rejected: {exc}")
                continue

            print(f"[CLIENT] Received Packet : {packet.packet_type}")

            # -----------------------------
            # Key-Pair (Kyber) Rotation for forward secrecy
            # -----------------------------
            if ForwardSecrecy.should_rehandshake(session):
                await request_keypair_rotation(writer, session, peer)

            # -----------------------------
            # Handle RESUME Response
            # -----------------------------
            if packet.packet_type == MessageType.RESUME:
                print()
                print("========== SESSION RESUME ==========")
                print("Secure session resumed")
                print("====================================")

                resume_ack = ResumeMessage.decode(packet.payload)

                session.crypto.load_shared_secret(
                    cache["shared_secret"],
                    is_client=True,
                    salt=bytes.fromhex(resume_ack.resume_salt),
                    version=cache["key_version"],
                )
                session.crypto.establish()
                session.set_state(SessionState.ESTABLISHED)

                metrics.resume_successful()

            # -----------------------------
            # Handle ERROR / Resume Failure
            # -----------------------------
            elif packet.packet_type == MessageType.ERROR:

                error = ErrorMessage.decode(packet.payload)

                print()
                print("========== ERROR ==========")
                print(error.message)
                print("============================")

                if error.code == 1:
                    print("[CLIENT] Resume failed, falling back to full handshake")

                    SessionCache.clear()
                    resume_mode = False
                    metrics.resume_failed_event()

                    print()
                    print("========== RESUME FALLBACK ==========")

                    # New session, old cache discarded
                    session = manager.create()

                    await send_hello(writer, session, peer)

                    print()
                    print("[CLIENT] HELLO re-sent for full handshake")
                    print("========================================")
                    continue

            # -----------------------------
            # Encrypted DATA Handling
            # -----------------------------
            elif packet.packet_type == MessageType.DATA:

                plaintext = CryptoEngine.decrypt(
                    session,
                    packet.payload,
                )

                print()
                print("========== Agent B ==========")
                print(plaintext.decode())
                print("=============================")

                # Don't reply during re-handshake
                if session.rehandshaking:
                    print("[CLIENT] Waiting for new Kyber handshake...")
                    continue

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

                print(f"[CLIENT] Messages Exchanged: {message_count}/{MAX_MESSAGES}")
                if message_count >= MAX_MESSAGES:
                    print("\nConversation Finished")
                    break
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

                reply = agent_a.chat(
                    "Say hello to another AI agent in one short sentence."
                )

                print()
                print("Agent A:", reply)
                print()

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

                data_sent = True

                await asyncio.sleep(2)

        if heartbeat_task and not heartbeat_task.done():
            heartbeat_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await heartbeat_task

        writer.close()

        # NOTE: aioquic's writer.wait_closed() does not resolve until the whole
        # QUIC connection closes; the `async with connect(...)` context manager
        # closes the connection (and its streams) on exit.
        print("[CLIENT] Connection Closing")
        print()
        metrics.print()

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())