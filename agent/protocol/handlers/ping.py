from agent.protocol.handlers.base import PacketHandler

from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType

from agent.protocol.payloads.ping import PingMessage
from agent.protocol.payloads.pong import PongMessage
from agent.metrics import metrics

class PingHandler(PacketHandler):

    def handle(self, session, packet):

        if not session.is_established():
            return None

        session.touch()

        message = PingMessage.decode(
            packet.payload
        )
        metrics.pings+=1
        print()
        print("========== PING ==========")
        print(
            f"Timestamp : {message.timestamp}"
        )
        print("==========================")

        response = PongMessage(
            message.timestamp
        )

        return Packet(
            packet_type=MessageType.PONG,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=response.encode(),
        )