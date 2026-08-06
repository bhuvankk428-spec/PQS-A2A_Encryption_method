from agent.protocol.messages import MessageType

from agent.protocol.handlers.hello import HelloHandler
from agent.protocol.handlers.hello_ack import HelloAckHandler
from agent.protocol.handlers.kyber_public_key import KyberPublicKeyHandler
from agent.protocol.handlers.kyber_ciphertext import KyberCiphertextHandler
from agent.protocol.handlers.key_confirm import KeyConfirmHandler
from agent.protocol.handlers.data import DataHandler


class ProtocolEngine:

    handlers = {

        MessageType.HELLO: HelloHandler(),

        MessageType.HELLO_ACK: HelloAckHandler(),

        MessageType.KYBER_PUBLIC_KEY: KyberPublicKeyHandler(),

        MessageType.KYBER_CIPHERTEXT: KyberCiphertextHandler(),

        MessageType.KEY_CONFIRM: KeyConfirmHandler(),

        MessageType.DATA: DataHandler(),
    }

    @classmethod
    def process(cls, session, packet):

        handler = cls.handlers.get(packet.packet_type)

        if handler is None:
            print("Unknown packet")
            return None

        return handler.handle(session, packet)