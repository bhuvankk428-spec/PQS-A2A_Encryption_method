from agent.protocol.handlers.base import PacketHandler
from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType

from agent.protocol.payloads.ping import PingMessage
from agent.protocol.payloads.pong import PongMessage

from agent.metrics import metrics

from monitor.events import protocol_event

class PingHandler(PacketHandler):

    def handle(self, session, packet):

        # Session must already be established
        if not session.is_established():
            return None

        session.touch()

        # Decode incoming PING
        message = PingMessage.decode(packet.payload)

        metrics.pings += 1

        print()
        print("========== PING ==========")
        print(f"Timestamp : {message.timestamp}")
        print("==========================")

        protocol_event(
            "PING",
            "SERVER",
            "PING received",
            timestamp=message.timestamp,
            session=str(session.session_id),
        )

        # Build PONG response
        response = PongMessage(
            message.timestamp
        )

        protocol_event(
            "PONG",
            "SERVER",
            "Sending PONG",
            timestamp=message.timestamp,
            session=str(session.session_id),
        )

        return Packet(
            packet_type=MessageType.PONG,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=response.encode(),
        )