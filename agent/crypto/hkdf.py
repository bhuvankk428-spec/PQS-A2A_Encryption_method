from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class KeyDerivation:

    @staticmethod
    def derive(shared_secret: bytes):

        hkdf = HKDF(
            algorithm=hashes.SHA384(),
            length=64,
            salt=None,
            info=b"SPQ-A2A Session Keys",
        )

        key_material = hkdf.derive(shared_secret)

        send_key = key_material[:32]

        receive_key = key_material[32:]

        return send_key, receive_key