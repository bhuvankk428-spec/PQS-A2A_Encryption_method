from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType
from agent.protocol.state import SessionState

from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.hello import HelloMessage
from agent.protocol.payloads.kyber_public_key import KyberPublicKeyMessage

from agent.crypto.ml_kem import MLKEM
from agent.protocol.handlers.base import PacketHandler

class HelloHandler(PacketHandler):

    def handle(self, session, packet):

        # Allow:
        # 1. Brand new sessions
        # 2. Existing sessions performing a forward-secrecy re-handshake
        if (
            session.state != SessionState.NEW
            and not session.rehandshaking
        ):
            return None

        # Decode HELLO
        hello = HelloMessage.decode(packet.payload)

        if session.rehandshaking:
            print()
            print("===== FORWARD SECRECY =====")
            print("Starting fresh Kyber exchange")
            print("===========================")
        else:
            print(f"HELLO received from {hello.peer_id}")

        # --------------------------------------------------
        # Generate NEW ML-KEM keypair
        # --------------------------------------------------

        kem = MLKEM()

        public_key = kem.generate_keypair()

        # Replace old keypair
        session.crypto.public_key = kem.public_key
        session.crypto.private_key = kem.private_key

        # Update state
        session.set_state(SessionState.HELLO_RECEIVED)

        # --------------------------------------------------
        # Build KYBER_PUBLIC_KEY packet
        # --------------------------------------------------

        payload = KyberPublicKeyMessage(
            peer_id=hello.peer_id,
            public_key=public_key,
        ).encode()

        return Packet(
            packet_type=MessageType.KYBER_PUBLIC_KEY,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=payload,
        )