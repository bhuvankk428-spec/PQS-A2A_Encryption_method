from agent.protocol.handlers.base import PacketHandler
from agent.protocol.packet import Packet
from agent.protocol.messages import MessageType
from agent.protocol.state import SessionState

from agent.protocol.payloads.kyber_ciphertext import KyberCiphertextMessage
from agent.protocol.payloads.key_confirm import KeyConfirmMessage

from agent.crypto.ml_kem import MLKEM

from agent.session import store
from agent.session.ticket import SessionTicket
from agent.metrics import metrics
from monitor.events import protocol_event


class KyberCiphertextHandler(PacketHandler):

    def handle(self, session, packet):

        # Server must have already sent its Kyber public key
        if session.state != SessionState.HELLO_RECEIVED:
            return None

        message = KyberCiphertextMessage.decode(packet.payload)

        print("Received KYBER_CIPHERTEXT")

        protocol_event(
            "KYBER_CIPHERTEXT",
            "SERVER",
            "Kyber ciphertext received",
        )

        # --------------------------------------------------
        # Recover shared secret
        # --------------------------------------------------
        kem = MLKEM()
        kem.private_key = session.crypto.private_key

        shared_secret = kem.decapsulate(
            message.ciphertext
        )

        session.crypto.ciphertext = message.ciphertext
        session.is_client = False

        session.crypto.load_shared_secret(
            shared_secret,
            is_client=False,
        )

        print("Shared Secret Recovered")
        print("AES Keys Derived")

        protocol_event(
            "SHARED_SECRET",
            "SERVER",
            "Shared secret recovered",
        )

        # Activate encryption
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
                "SERVER",
                "Fresh session keys installed",
            )

            session.rehandshaking = False

            session.crypto.messages_sent = 0
            session.crypto.messages_received = 0

        session.set_state(SessionState.ESTABLISHED)

        # Handshake (or key-pair rotation) completed on the server side
        metrics.handshakes += 1
        metrics.finish_handshake()

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
        print("===== SERVER STORE AFTER SAVE =====")
        print(store.tickets.keys())
        print("===================================")

        protocol_event(
            "SESSION_STORE",
            "SERVER",
            "Session ticket stored",
        )

        # --------------------------------------------------
        # Send KEY_CONFIRM
        # --------------------------------------------------
        payload = KeyConfirmMessage(
            success=True,
        ).encode()

        protocol_event(
            "KEY_CONFIRM",
            "SERVER",
            "Sending KEY_CONFIRM",
        )

        return Packet(
            packet_type=MessageType.KEY_CONFIRM,
            session_id=session.session_id,
            sequence=session.next_send_sequence(),
            payload=payload,
        )