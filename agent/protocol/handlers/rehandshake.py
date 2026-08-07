from agent.protocol.handlers.base import PacketHandler
from agent.protocol.state import SessionState

from monitor.events import protocol_event
class ReHandshakeHandler(PacketHandler):

    def handle(self, session, packet):

        print()
        print("===== FORWARD SECRECY =====")
        print("REHANDSHAKE requested")
        print("===========================")

        protocol_event(
            "REHANDSHAKE",
            "SERVER",
            "Forward Secrecy requested",
            session=str(session.session_id),
        )

        # Enable re-handshake mode
        session.rehandshaking = True

        # Reset counters for the next key epoch
        session.crypto.messages_sent = 0
        session.crypto.messages_received = 0

        # Wait for a fresh HELLO packet
        session.set_state(SessionState.NEW)

        return None