from agent.protocol.messages import MessageType

from agent.protocol.handlers.hello import HelloHandler
from agent.protocol.handlers.hello_ack import HelloAckHandler
from agent.protocol.handlers.kyber_public_key import KyberPublicKeyHandler
from agent.protocol.handlers.kyber_ciphertext import KyberCiphertextHandler
from agent.protocol.handlers.key_confirm import KeyConfirmHandler
from agent.protocol.handlers.data import DataHandler
from agent.protocol.handlers.rekey import RekeyHandler
from agent.protocol.handlers.error import ErrorHandler
from agent.protocol.handlers.resume import ResumeHandler
from agent.protocol.handlers.ping import PingHandler
from agent.protocol.handlers.pong import PongHandler
from agent.metrics import metrics
from agent.protocol.handlers.rehandshake import ReHandshakeHandler
class ProtocolEngine:
    
    handlers = {

        MessageType.HELLO: HelloHandler(),

        MessageType.HELLO_ACK: HelloAckHandler(),

        MessageType.KYBER_PUBLIC_KEY: KyberPublicKeyHandler(),

        MessageType.KYBER_CIPHERTEXT: KyberCiphertextHandler(),

        MessageType.KEY_CONFIRM: KeyConfirmHandler(),

        MessageType.DATA: DataHandler(),

        MessageType.REHANDSHAKE: ReHandshakeHandler(),
        MessageType.REKEY: RekeyHandler(),

        MessageType.ERROR: ErrorHandler(),

        MessageType.RESUME: ResumeHandler(),
       
        MessageType.PING: PingHandler(),

        MessageType.PONG: PongHandler(),
    }

    @classmethod
    def process(cls, session, packet):
        handler = cls.handlers.get(packet.packet_type)

        if handler is None:

            print(
                f"[ERROR] Unknown Packet Type : "
                f"{packet.packet_type}"
            )

            return None

        try:

            return handler.handle(
                session,
                packet,
            )

        except Exception as e:

            print()
            print("========== PROTOCOL ERROR ==========")
            print(type(e).__name__)
            print(e)
            print("====================================")

            return None