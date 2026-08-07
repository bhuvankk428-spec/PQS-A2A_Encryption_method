from agent.crypto.engine import CryptoEngine
import time
from agent.protocol.handlers.base import PacketHandler
from agent.protocol.messages import MessageType
from agent.protocol.packet import Packet
from agent.ai.model import AIModel
from monitor.events import protocol_event
agent_b = AIModel("Agent B")

class DataHandler(PacketHandler):

    def handle(self, session, packet):

        # Session must already exist
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

        protocol_event(
            "DATA",
            "SERVER",
            "Message decrypted",
            plaintext=plaintext.decode(),
            ciphertext=packet.payload.hex(),
            session=str(session.session_id),
        )

        reply = agent_b.chat(
                    f"""
                You are Agent B.

                You are communicating with Agent A through a secure quantum-encrypted protocol.

                Your reply must:
                - be ONE sentence only
                - be under 15 words
                - never use markdown
                - never use bullet points
                - never say "I didn't understand"
                - continue the conversation naturally

                Agent A said:
                {plaintext.decode()}
                """
                )
        reply = reply.strip()

        if (
            len(reply) < 5
            or "didn't understand" in reply.lower()
            or "*" in reply
        ):
            reply = "Tell me something about our secure protocol."        

        print(f"\n[Agent B]\n{reply}\n")
        time.sleep(3)
        response = CryptoEngine.encrypt(
            session,
            reply.encode(),
        )

        protocol_event(
            "DATA",
            "SERVER",
            "Encrypted reply sent",
            session=str(session.session_id),
        )

        return Packet(
            packet_type=MessageType.DATA,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=response,
        )