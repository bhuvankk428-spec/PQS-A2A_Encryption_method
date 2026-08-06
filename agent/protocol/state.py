from enum import Enum, auto


class SessionState(Enum):

    NEW = auto()

    HELLO_SENT = auto()

    HELLO_RECEIVED = auto()

    HANDSHAKE_COMPLETE = auto()

    ESTABLISHED = auto()

    REKEYING = auto()
    
    CLOSED = auto()