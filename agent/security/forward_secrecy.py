import time

from agent.config import MAJOR_KEY_LIFETIME


class ForwardSecrecy:

    ROTATION_INTERVAL = 10

    MAJOR_KEY_LIFETIME = MAJOR_KEY_LIFETIME

    @staticmethod
    def should_rehandshake(session):

        return (
            session.is_established()
            and not session.rehandshaking
            and time.time() - session.major_established_at
            >= ForwardSecrecy.MAJOR_KEY_LIFETIME
        )
