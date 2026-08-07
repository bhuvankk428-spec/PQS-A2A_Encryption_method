from agent.crypto.cipher import Cipher
from agent.security.rotation import KeyRotation
from agent.metrics import metrics

class CryptoEngine:

    @staticmethod
    def encrypt(session, plaintext: bytes):

        if session.crypto.send_key is None:
            raise RuntimeError(
                "Encryption key not established"
            )

        # Rotation is now handled by the protocol layer.
# CryptoEngine only encrypts/decrypts.
        
        nonce = session.crypto.next_nonce()

        cipher = Cipher(
            session.crypto.send_key
        )

        ciphertext = cipher.encrypt(
            nonce,
            plaintext,
        )

        session.crypto.sent()
        metrics.encrypted_messages += 1
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
        metrics.decrypted_messages += 1
        return plaintext