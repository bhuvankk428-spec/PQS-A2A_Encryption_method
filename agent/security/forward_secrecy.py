class ForwardSecrecy:

    ROTATION_INTERVAL = 10

    @staticmethod
    def should_rehandshake(session):

        return (
            session.is_established()
            and not session.rehandshaking
            and session.crypto.messages_sent >= ForwardSecrecy.ROTATION_INTERVAL
        )