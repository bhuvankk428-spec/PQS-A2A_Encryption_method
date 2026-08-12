from agent.crypto.hkdf import KeyDerivation


class KeyRotation:

    # Rotate AES keys every N encrypted messages (version-based derivation
    # from the SAME shared secret). Note: this is key *diversification* only.
    # To actually discard the old shared secret (real forward secrecy and
    # mitigation of long-term kyber key-pair exposure / side-channels) a fresh
    # ML-KEM key-pair rotation is needed -- see agent.security.forward_secrecy.
    ROTATION_INTERVAL = 25

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

        session.crypto.install_keys(
            key1,
            key2,
            session.is_client,
        )
        session.crypto.key_version = next_version

        print(
            f"New Key Version : "
            f"{session.crypto.key_version}"
        )
        print("==============================")

    @staticmethod
    def next_version(session):

        return session.crypto.key_version + 1