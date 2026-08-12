import time

from agent.protocol.constants import PROTOCOL_VERSION


class ForwardSecrecy:

    # Number of encrypted messages per key epoch. When crossed, the agent
    # performs a FULL ML-KEM key-pair rotation (a fresh Kyber handshake),
    # which discards the old shared secret.
    ROTATION_INTERVAL = 4

    # Fallback time-based rotation so long-idle sessions still rotate.
    ROTATION_TIMEOUT = 60

    @staticmethod
    def should_rehandshake(session):

        return (
            session.is_established()
            and not session.rehandshaking
            and (
                session.crypto.messages_sent >= ForwardSecrecy.ROTATION_INTERVAL
                or (
                    time.time() - session.last_rehandshake
                    >= ForwardSecrecy.ROTATION_TIMEOUT
                )
            )
        )