from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType
from agent.protocol.state import SessionState

from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.hello import HelloMessage
from agent.protocol.payloads.kyber_public_key import KyberPublicKeyMessage

from agent.crypto.ml_kem import MLKEM


class HelloHandler(PacketHandler):

    def handle(self, session, packet):

        if session.state != SessionState.NEW:
            return None

        # Decode HELLO
        hello = HelloMessage.decode(packet.payload)

        print(f"HELLO received from {hello.peer_id}")

        # --------------------------------------------------
        # Generate ML-KEM keypair
        # --------------------------------------------------

        kem = MLKEM()

        public_key = kem.generate_keypair()

        # Store in CryptoContext
        session.crypto.public_key = kem.public_key
        session.crypto.private_key = kem.private_key

        # Update state
        session.set_state(SessionState.HELLO_RECEIVED)

        # --------------------------------------------------
        # Build KYBER_PUBLIC_KEY payload
        # --------------------------------------------------

        payload = KyberPublicKeyMessage(
            peer_id=hello.peer_id,
            public_key=public_key,
        ).encode()
        print("Payload Length:", len(payload))
        print(payload)
        return Packet(
            packet_type=MessageType.KYBER_PUBLIC_KEY,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=payload,
        )