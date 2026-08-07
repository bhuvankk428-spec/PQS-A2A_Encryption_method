from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType
from agent.protocol.state import SessionState
from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.hello import HelloMessage
from agent.protocol.payloads.kyber_public_key import KyberPublicKeyMessage

from agent.crypto.ml_kem import MLKEM

from monitor.events import protocol_event
class HelloHandler(PacketHandler):

    def handle(self, session, packet):

        # Allow:
        # 1. Brand new sessions
        # 2. Existing sessions performing Forward Secrecy re-handshake
        if (
            session.state != SessionState.NEW
            and not session.rehandshaking
        ):
            return None

        # Decode HELLO
        hello = HelloMessage.decode(packet.payload)

        protocol_event(
            "HELLO",
            "SERVER",
            "HELLO received",
            peer=hello.peer_id,
            session=str(session.session_id),
        )

        if session.rehandshaking:
            print()
            print("===== FORWARD SECRECY =====")
            print("Starting fresh Kyber exchange")
            print("===========================")

            protocol_event(
                "REHANDSHAKE",
                "SERVER",
                "Starting fresh Kyber exchange",
                session=str(session.session_id),
            )
        else:
            print(f"HELLO received from {hello.peer_id}")

        # ------------------------------------------
        # Generate NEW ML-KEM keypair
        # ------------------------------------------

        kem = MLKEM()

        public_key = kem.generate_keypair()

        # Store keypair
        session.crypto.public_key = kem.public_key
        session.crypto.private_key = kem.private_key

        # Move protocol state
        session.set_state(SessionState.HELLO_RECEIVED)

        # ------------------------------------------
        # Build KYBER_PUBLIC_KEY
        # ------------------------------------------

        payload = KyberPublicKeyMessage(
            peer_id=hello.peer_id,
            public_key=public_key,
        ).encode()

        protocol_event(
            "KYBER_PUBLIC_KEY",
            "SERVER",
            "Public key sent",
            session=str(session.session_id),
        )

        return Packet(
            packet_type=MessageType.KYBER_PUBLIC_KEY,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=payload,
        )