from agent.crypto.hkdf import KeyDerivation


class KeyRotation:

    # Rotate after every 1000 encrypted messages
    ROTATION_INTERVAL = 1

    @staticmethod
    def should_rotate(session) -> bool:

        return (
            session.crypto.messages_sent > 0
            and
            session.crypto.messages_sent %
            KeyRotation.ROTATION_INTERVAL == 0
        )

    @staticmethod
    def rotate(session):

        print()
        print("========== KEY ROTATION ==========")

        next_version = (
    session.crypto.key_version + 1
)

        key1, key2 = KeyDerivation.derive(
    session.crypto.shared_secret,
    version=next_version,
)

        if session.is_client:

            session.crypto.send_key = key1
            session.crypto.receive_key = key2

        else:

            session.crypto.send_key = key2
            session.crypto.receive_key = key1

        session.crypto.key_version = next_version

        print(
            f"New Key Version : "
            f"{session.crypto.key_version}"
        )

        print("==============================")

    @staticmethod
    def next_version(session):

        return session.crypto.key_version + 1