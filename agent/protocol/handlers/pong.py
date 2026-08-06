from time import time

from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.pong import PongMessage


class PongHandler(PacketHandler):

    def handle(self, session, packet):

        if not session.is_established():
            return None

        session.touch()

        message = PongMessage.decode(
            packet.payload
        )

        rtt = (
            time() - message.timestamp
        ) * 1000

        print()
        print("========== PONG ==========")
        print(f"RTT : {rtt:.2f} ms")
        print("==========================")

        return None