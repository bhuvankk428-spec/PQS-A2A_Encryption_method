from time import time

from agent.protocol.handlers.base import PacketHandler
from agent.protocol.payloads.pong import PongMessage

from agent.metrics import metrics
from monitor.events import protocol_event

class PongHandler(PacketHandler):

    def handle(self, session, packet):

        if not session.is_established():
            return None

        session.touch()

        message = PongMessage.decode(packet.payload)

        rtt = (time() - message.timestamp) * 1000

        metrics.pongs += 1

        print()
        print("========== PONG ==========")
        print(f"RTT : {rtt:.2f} ms")
        print("==========================")

        protocol_event(
            "PONG",
            "CLIENT",
            "PONG received",
            rtt=f"{rtt:.2f} ms",
            session=str(session.session_id),
        )

        return None