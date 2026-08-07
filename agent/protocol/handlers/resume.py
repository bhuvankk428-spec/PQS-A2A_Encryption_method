from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.resume import ResumeMessage

from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType
from agent.protocol.state import SessionState

from agent.session import store
from agent.metrics import metrics
from monitor.events import protocol_event

class ResumeHandler(PacketHandler):

    def handle(self, session, packet):

        message = ResumeMessage.decode(
            packet.payload
        )

        print()
        print("========== SESSION RESUME ==========")
        print("Requested:", message.session_id)

        protocol_event(
            "SESSION_RESUME",
            "SERVER",
            "Resume requested",
            requested_session=message.session_id,
        )

        ticket = store.get(
            message.session_id
        )

        print()
        print("===== STORE BEFORE RESUME =====")
        print(store)
        print(store.tickets.keys())
        print("===============================")

        # ---------------------------------------
        # Resume Failed
        # ---------------------------------------
        if ticket is None:

            print("Resume Failed")
            print("===========================")

            metrics.resume_failed += 1

            protocol_event(
                "SESSION_RESUME",
                "SERVER",
                "Resume failed",
                requested_session=message.session_id,
            )

            return None

        # ---------------------------------------
        # Resume Success
        # ---------------------------------------
        print("Resume Success")

        metrics.resume_success += 1

        session.crypto.load_shared_secret(
            ticket.shared_secret,
            is_client=session.is_client,
        )

        session.crypto.key_version = ticket.key_version
        session.crypto.establish()

        session.set_state(
            SessionState.ESTABLISHED
        )

        session.touch()

        print(
            f"Key Version : {session.crypto.key_version}"
        )

        print("===========================")

        protocol_event(
            "SESSION_RESUME",
            "SERVER",
            "Session resumed successfully",
            session=str(session.session_id),
            key_version=session.crypto.key_version,
        )

        # ---------------------------------------
        # Send Resume ACK
        # ---------------------------------------
        response = ResumeMessage(
            str(session.session_id)
        )

        protocol_event(
            "SESSION_RESUME_ACK",
            "SERVER",
            "Sending Resume ACK",
            session=str(session.session_id),
        )

        return Packet(
            packet_type=MessageType.RESUME,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=response.encode(),
        )