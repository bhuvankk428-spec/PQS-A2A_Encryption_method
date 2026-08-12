from agent.protocol.messages import MessageType


PROTOCOL_VERSION = 1

# Packet Types (single source of truth lives in messages.MessageType)
HELLO = int(MessageType.HELLO)
HELLO_ACK = int(MessageType.HELLO_ACK)
CLIENT_READY = int(MessageType.CLIENT_READY)
SERVER_READY = int(MessageType.SERVER_READY)

KYBER_PUBLIC_KEY = int(MessageType.KYBER_PUBLIC_KEY)
KYBER_CIPHERTEXT = int(MessageType.KYBER_CIPHERTEXT)
KEY_CONFIRM = int(MessageType.KEY_CONFIRM)

DATA = int(MessageType.DATA)

REKEY = int(MessageType.REKEY)
RESUME = int(MessageType.RESUME)
CLOSE = int(MessageType.CLOSE)

PING = int(MessageType.PING)
PONG = int(MessageType.PONG)

REHANDSHAKE = int(MessageType.REHANDSHAKE)

ERROR = int(MessageType.ERROR)

# Flags
FLAG_NONE = 0x00
FLAG_ENCRYPTED = 0x01
FLAG_ACK_REQUIRED = 0x02