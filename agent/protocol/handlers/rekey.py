from agent.protocol.handlers.base import PacketHandler
from agent.protocol.payloads.rekey import RekeyMessage

from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType

from agent.security.rotation import KeyRotation
from agent.metrics import metrics


class RekeyHandler(PacketHandler):

    def handle(self, session, packet):

        message = RekeyMessage.decode(
            packet.payload
        )

        print()
        print("========== REKEY ==========")
        print(
            f"Received Key Version : "
            f"{message.key_version}"
        )

        # ACK received
        if message.acknowledge:

            print("Rekey completed.")
            print("===========================")

            return None

        # Rotate locally
        KeyRotation.rotate(session)

        metrics.rekeys += 1

        print(
            f"Current Version : "
            f"{session.crypto.key_version}"
        )

        print("===========================")

        # Send ACK

        ack = RekeyMessage(
            key_version=session.crypto.key_version,
            acknowledge=True,
        )

        return Packet(
            packet_type=MessageType.REKEY,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=ack.encode(),
        )