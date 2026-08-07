from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType
from agent.protocol.state import SessionState
from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.kyber_public_key import KyberPublicKeyMessage
from agent.protocol.payloads.kyber_ciphertext import KyberCiphertextMessage

from agent.crypto.ml_kem import MLKEM


class KyberPublicKeyHandler(PacketHandler):

    def handle(self, session, packet):

        # Allow initial handshake and forward-secrecy re-handshake
        if (session.state != SessionState.HELLO_SENT and not session.rehandshaking):
            return None

        # Decode the server's ML-KEM public key
        message = KyberPublicKeyMessage.decode(packet.payload)

        print("Received KYBER_PUBLIC_KEY")

        # Encapsulate using the server's public key
        kem = MLKEM()

        ciphertext, shared_secret = kem.encapsulate(
            message.public_key
        )

       # Store ciphertext
        session.crypto.ciphertext = ciphertext

# Mark this session as the client
        session.is_client = True

# Derive directional AES-256 session keys
        session.crypto.load_shared_secret(
    shared_secret,
    is_client=True,
)
        print("Shared secret established.")
        print("AES session keys derived.")

        # Build KYBER_CIPHERTEXT payload
        response = KyberCiphertextMessage(
            ciphertext=ciphertext
        )

        return Packet(
            packet_type=MessageType.KYBER_CIPHERTEXT,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=response.encode(),
        )