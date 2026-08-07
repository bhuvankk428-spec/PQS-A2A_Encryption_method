from agent.crypto.engine import CryptoEngine
from agent.protocol.handlers.base import PacketHandler
from agent.protocol.messages import MessageType
from agent.protocol.packet import Packet


class DataHandler(PacketHandler):

    def handle(self, session, packet):
        # 1. Ensure session active & touch session timer
        if not session.is_established():
            return None

        session.touch()

        # 2. Decrypt incoming DATA payload
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

        # 3. Encrypt and return standard server reply
        response = CryptoEngine.encrypt(
            session,
            b"Hello Client, Secure Message Received!",
        )

        return Packet(
            packet_type=MessageType.DATA,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=response,
        )