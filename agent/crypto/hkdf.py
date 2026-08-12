from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class KeyDerivation:

    @staticmethod
    def derive(
        shared_secret: bytes,
        version: int = 1,
    ):

        hkdf = HKDF(
            algorithm=hashes.SHA384(),
            length=64,
            salt=None,
            info=f"SPQ-A2A Session Keys v{version}".encode(),
        )

        key_material = hkdf.derive(
            shared_secret
        )

        send_key = key_material[:32]

        receive_key = key_material[32:]

        return send_key, receive_key

    @staticmethod
    def derive_resume(
        shared_secret: bytes,
        salt: bytes,
        version: int = 1,
    ):

        # A fresh random salt per resumed connection produces a fresh pair of
        # AES keys even when the long-lived master secret is unchanged. This
        # is what prevents AES-GCM nonce reuse across resumed sessions.
        hkdf = HKDF(
            algorithm=hashes.SHA384(),
            length=64,
            salt=salt,
            info=f"SPQ-A2A Resume Keys v{version}".encode(),
        )

        key_material = hkdf.derive(
            shared_secret
        )

        send_key = key_material[:32]

        receive_key = key_material[32:]

        return send_key, receive_key