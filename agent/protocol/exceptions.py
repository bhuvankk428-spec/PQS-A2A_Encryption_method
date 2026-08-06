class ProtocolError(Exception):
    """Base protocol exception."""


class InvalidPacketError(ProtocolError):
    """Packet is malformed."""


class ReplayAttackError(ProtocolError):
    """Replay attack detected."""


class CryptoError(ProtocolError):
    """Cryptographic failure."""


class HandshakeError(ProtocolError):
    """Handshake failure."""