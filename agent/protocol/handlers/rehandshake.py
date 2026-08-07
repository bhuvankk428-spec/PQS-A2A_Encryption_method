from agent.protocol.handlers.base import PacketHandler
from agent.protocol.state import SessionState


class ReHandshakeHandler(PacketHandler):

    def handle(self, session, packet):

        print()
        print("===== FORWARD SECRECY =====")
        print("REHANDSHAKE requested")
        print("===========================")

        session.rehandshaking = True

        # Reset counters for the next key epoch
        session.crypto.messages_sent = 0
        session.crypto.messages_received = 0

        # Prepare to receive a fresh HELLO
        session.set_state(SessionState.HELLO_RECEIVED)

        return None