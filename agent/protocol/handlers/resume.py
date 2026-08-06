from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.resume import ResumeMessage

from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType
from agent.protocol.state import SessionState

from agent.session import store


class ResumeHandler(PacketHandler):
    def handle(self, session, packet):
        message = ResumeMessage.decode(
            packet.payload
        )

        print()
        print("========== SESSION RESUME ==========")
        print(
            "Requested:",
            message.session_id
        )

        ticket = store.get(
            message.session_id
        )

        if ticket is None:
            print("Resume Failed")
            print("===========================")
            return None

        print("Resume Success")

        session.crypto.load_shared_secret(
            ticket.shared_secret,
            is_client=session.is_client,
        )

        session.set_state(
            SessionState.ESTABLISHED
        )

        session.touch()

        print(
            f"Key Version : {session.crypto.key_version}"
        )

        print("===========================")

        response = ResumeMessage(
            str(session.session_id)
        )

        return Packet(
            packet_type=MessageType.RESUME,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=response.encode(),
        )