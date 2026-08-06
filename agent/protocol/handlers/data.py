from agent.protocol.handlers.base import PacketHandler

from agent.crypto.engine import CryptoEngine

from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType


class DataHandler(PacketHandler):

    def handle(self, session, packet):

        # Session must be established
        if not session.is_established():
            return None

        session.touch()

        try:

            plaintext = CryptoEngine.decrypt(
                session,
                packet.payload,
            )

        except Exception:

            print("[SECURITY] Invalid ciphertext")

            return None

        print()
        print("========== SECURE DATA ==========")
        print(plaintext.decode())
        print("=================================")

        response = CryptoEngine.encrypt(
            session,
            b"Hello Client, Secure Message Received!"
        )

        return Packet(
            packet_type=MessageType.DATA,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=response,
        )