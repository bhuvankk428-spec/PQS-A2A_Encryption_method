from agent.protocol.handlers.base import PacketHandler
from agent.protocol.state import SessionState

from agent.protocol.payloads.key_confirm import KeyConfirmMessage

from agent.session import store
from agent.session.ticket import SessionTicket
from agent.session.cache import SessionCache
from monitor.events import protocol_event


class KeyConfirmHandler(PacketHandler):

    def handle(self, session, packet):

        # Client must have already received the server's public key
        if session.state != SessionState.HELLO_SENT:
            return None

        message = KeyConfirmMessage.decode(packet.payload)

        if not message.success:
            print("Key confirmation failed.")

            protocol_event(
                "KEY_CONFIRM",
                "CLIENT",
                "Key confirmation failed",
            )

            return None

        print("KEY_CONFIRM received.")
        print("Secure session established.")

        protocol_event(
            "KEY_CONFIRM",
            "CLIENT",
            "Secure session established",
        )

        # Activate AES session
        session.crypto.establish()

        # --------------------------------------------------
        # Forward Secrecy completed
        # --------------------------------------------------
        if session.rehandshaking:

            print()
            print("===== FORWARD SECRECY COMPLETE =====")
            print("Fresh Kyber keys installed")
            print("Old shared secret discarded")
            print("====================================")

            protocol_event(
                "FORWARD_SECRECY",
                "CLIENT",
                "Fresh session keys installed",
            )

            session.rehandshaking = False
            session.forward_secrecy_complete = True

            # Reset counters for the new key epoch
            session.crypto.messages_sent = 0
            session.crypto.messages_received = 0

            # Tell the client loop to resume sending messages
            session.send_after_rehandshake = True

        # Session is now active
        session.set_state(SessionState.ESTABLISHED)

        # --------------------------------------------------
        # Save session ticket
        # --------------------------------------------------
        ticket = SessionTicket(
            session_id=str(session.session_id),
            shared_secret=session.crypto.shared_secret,
            key_version=session.crypto.key_version,
        )

        store.save(ticket)

        print()
        print("===== STORE AFTER SAVE =====")
        print(store)
        print(store.tickets.keys())
        print("============================")

        # --------------------------------------------------
        # Save resume cache
        # --------------------------------------------------
        SessionCache.save(
            str(session.session_id),
            session.crypto.shared_secret,
            session.crypto.key_version,
        )

        print("[CLIENT] Session Cache Saved")
        print("[SESSION] Ticket Saved")

        protocol_event(
            "SESSION_CACHE",
            "CLIENT",
            "Session cached for resumption",
        )

        # No packet needs to be sent after KEY_CONFIRM
        return None