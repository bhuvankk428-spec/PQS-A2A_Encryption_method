from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType
from agent.protocol.state import SessionState
from agent.protocol.handlers.base import PacketHandler

from agent.protocol.payloads.key_confirm import KeyConfirmMessage
from agent.session import store
from agent.session.ticket import SessionTicket
from agent.session.cache import SessionCache

class KeyConfirmHandler(PacketHandler):

    def handle(self, session, packet):

        # Client should have already derived the shared secret
        if session.state != SessionState.HELLO_SENT:
            return None

        # Decode KEY_CONFIRM
        message = KeyConfirmMessage.decode(packet.payload)

        if not message.success:
            print("Key confirmation failed.")
            return None

        print("KEY_CONFIRM received.")
        print("Secure session established.")

        # Mark crypto as established
        session.crypto.establish()

        # Update session state
        session.set_state(SessionState.ESTABLISHED)
        ticket = SessionTicket(
    session_id=str(session.session_id),
    shared_secret=session.crypto.shared_secret,
)

        store.save(ticket)
        SessionCache.save(

        str(session.session_id),

    session.crypto.shared_secret,

    session.crypto.key_version,
)

        print("[CLIENT] Session Cache Saved") 

        print(
    "[SESSION] Ticket Saved"
)
        # Reply with HELLO_ACK
        return Packet(
            packet_type=MessageType.HELLO_ACK,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=b"HELLO_ACK",
        )