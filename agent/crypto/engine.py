from agent.crypto.cipher import Cipher
from agent.security.rotation import KeyRotation


class CryptoEngine:

    @staticmethod
    def encrypt(session, plaintext: bytes):

        if session.crypto.send_key is None:
            raise RuntimeError(
                "Encryption key not established"
            )

        if KeyRotation.should_rotate(session):
            KeyRotation.rotate(session)

        nonce = session.crypto.next_nonce()

        cipher = Cipher(
            session.crypto.send_key
        )

        ciphertext = cipher.encrypt(
            nonce,
            plaintext,
        )

        session.crypto.sent()

        return nonce + ciphertext

    @staticmethod
    def decrypt(session, payload: bytes):

        if session.crypto.receive_key is None:
            raise RuntimeError(
                "Decryption key not established"
            )

        nonce = payload[:12]
        ciphertext = payload[12:]

        cipher = Cipher(
            session.crypto.receive_key
        )

        plaintext = cipher.decrypt(
            nonce,
            ciphertext,
        )

        session.crypto.received()

        return plaintext