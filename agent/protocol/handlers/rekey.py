from agent.protocol.handlers.base import PacketHandler
from agent.protocol.payloads.rekey import RekeyMessage

from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType

from agent.security.rotation import KeyRotation


class RekeyHandler(PacketHandler):

    def handle(self, session, packet):

        message = RekeyMessage.decode(
            packet.payload
        )

        print()
        print("========== REKEY ==========")
        print(
            f"Received Key Version : {message.key_version}"
        )

        # Rotate local AES keys
        KeyRotation.rotate(session)

        print(
            f"Current Key Version : "
            f"{session.crypto.key_version}"
        )

        print("===========================")

        # Send acknowledgement
        response = RekeyMessage(
            session.crypto.key_version
        )

        return Packet(
            packet_type=MessageType.REKEY,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=response.encode(),
        )