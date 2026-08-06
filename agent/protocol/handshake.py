from agent.protocol.constants import HELLO, HELLO_ACK
from agent.protocol.state import SessionState


class Handshake:

    @staticmethod
    def process(session, packet):

        # Client -> Server
        if (
            session.state == SessionState.NEW
            and packet.packet_type == HELLO
        ):

            session.set_state(
                SessionState.HELLO_RECEIVED
            )

            return HELLO_ACK

        # Server -> Client
        if (
            session.state == SessionState.HELLO_SENT
            and packet.packet_type == HELLO_ACK
        ):

            session.set_state(
                SessionState.HANDSHAKE_COMPLETE
            )

            return None

        return None


        