from agent.protocol.handlers.base import PacketHandler

from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType

from agent.protocol.payloads.ping import PingMessage
from agent.protocol.payloads.pong import PongMessage


class PingHandler(PacketHandler):

    def handle(self, session, packet):

        if not session.is_established():
            return None

        session.touch()

        message = PingMessage.decode(
            packet.payload
        )

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