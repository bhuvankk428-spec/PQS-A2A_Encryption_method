from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType
from agent.protocol.state import SessionState
from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.kyber_ciphertext import KyberCiphertextMessage
from agent.protocol.payloads.key_confirm import KeyConfirmMessage

from agent.crypto.ml_kem import MLKEM


class KyberCiphertextHandler(PacketHandler):

    def handle(self, session, packet):

        if session.state != SessionState.HELLO_RECEIVED:
            return None

        message = KyberCiphertextMessage.decode(packet.payload)

        print("Received KYBER_CIPHERTEXT")

        kem = MLKEM()

        kem.private_key = session.crypto.private_key

        shared_secret = kem.decapsulate(
            message.ciphertext
        )

        session.crypto.ciphertext = message.ciphertext

        session.crypto.load_shared_secret(
            shared_secret,
            is_client=False,
        )

        print("Shared Secret Recovered")
        print("AES Keys Derived")

        session.set_state(
            SessionState.HANDSHAKE_COMPLETE
        )

        payload = KeyConfirmMessage(
            success=True
        ).encode()

        return Packet(
            packet_type=MessageType.KEY_CONFIRM,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=payload,
        )