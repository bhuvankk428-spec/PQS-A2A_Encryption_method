import time

from agent.config import (
    MINI_KEY_LIFETIME,
    MINI_KEY_MESSAGE_LIMIT,
)
from agent.crypto.hkdf import KeyDerivation


class KeyRotation:

    ROTATION_INTERVAL = MINI_KEY_MESSAGE_LIMIT

    ROTATION_LIFETIME = MINI_KEY_LIFETIME

    @staticmethod
    def should_rotate(session) -> bool:

        if (
            not session.is_established()
            or session.rehandshaking
            or session.rekey_pending
        ):
            return False

        crypto = session.crypto

        return (
            crypto.messages_since_rotation >= KeyRotation.ROTATION_INTERVAL
            or
            time.time() - crypto.key_rotated_at >= KeyRotation.ROTATION_LIFETIME
        )

    @staticmethod
    def rotate(session, version: int | None = None):

        current_version = session.crypto.key_version

        # Duplicate/old rotation requests are ignored
        if version is not None and version <= current_version:
            return current_version

        next_version = (
            current_version + 1
            if version is None
            else version
        )

        print()
        print("========== KEY ROTATION ==========")

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
        session.crypto.messages_since_rotation = 0
        session.crypto.key_rotated_at = time.time()

        print(
            f"New Key Version : "
            f"{session.crypto.key_version}"
        )

        print("==============================")

        return next_version

    @staticmethod
    def next_version(session):

        return session.crypto.key_version + 1
