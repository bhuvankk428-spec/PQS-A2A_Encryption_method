from enum import IntEnum


class MessageType(IntEnum):

    # Handshake
    HELLO = 1
    HELLO_ACK = 2
    CLIENT_READY = 3
    SERVER_READY = 4

    # Key Exchange
    KYBER_PUBLIC_KEY = 10
    KYBER_CIPHERTEXT = 11
    KEY_CONFIRM = 12

    # Secure Data
    DATA = 20

    # Session
    REKEY = 30
    RESUME = 31
    CLOSE = 32

    # Heartbeat
    PING = 40
    PONG = 41

    # Errors
    ERROR = 255