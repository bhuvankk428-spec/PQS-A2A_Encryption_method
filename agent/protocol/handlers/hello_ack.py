from agent.protocol.handlers.base import PacketHandler
from agent.protocol.state import SessionState


class HelloAckHandler(PacketHandler):

    def handle(self, session, packet):

        if session.state != SessionState.ESTABLISHED:
            return None

        print()

        print("================================")
        print("Handshake Finished Successfully")
        print("Secure Session Ready")
        print("================================")

        return None