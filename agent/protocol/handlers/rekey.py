from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.rekey import RekeyMessage

from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType

from agent.security.rotation import KeyRotation

from agent.metrics import metrics
from monitor.events import protocol_event


class RekeyHandler(PacketHandler):

    def handle(self, session, packet):

        message = RekeyMessage.decode(packet.payload)

        print()
        print("========== REKEY ==========")
        print(f"Received Key Version : {message.key_version}")

        protocol_event(
            "REKEY",
            "SERVER" if not session.is_client else "CLIENT",
            "REKEY received",
            key_version=message.key_version,
            session=str(session.session_id),
        )

        # -------------------------------
        # ACK received
        # -------------------------------
        if message.acknowledge:

            print("Rekey completed.")
            print("===========================")

            protocol_event(
                "REKEY_ACK",
                "SERVER" if not session.is_client else "CLIENT",
                "Rekey acknowledged",
                key_version=message.key_version,
            )

            return None

        # -------------------------------
        # Rotate local AES keys
        # -------------------------------
        KeyRotation.rotate(session)

        metrics.rekeys += 1

        print(f"Current Version : {session.crypto.key_version}")
        print("===========================")

        protocol_event(
            "KEY_ROTATION",
            "SERVER" if not session.is_client else "CLIENT",
            "AES keys rotated",
            key_version=session.crypto.key_version,
        )

        # -------------------------------
        # Send ACK
        # -------------------------------
        ack = RekeyMessage(
            key_version=session.crypto.key_version,
            acknowledge=True,
        )

        protocol_event(
            "REKEY_ACK",
            "SERVER" if not session.is_client else "CLIENT",
            "Sending REKEY ACK",
            key_version=session.crypto.key_version,
        )

        return Packet(
            packet_type=MessageType.REKEY,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=ack.encode(),
        )