from agent.crypto.cipher import Cipher


class CryptoEngine:

    @staticmethod
    def encrypt(session, plaintext: bytes):

        cipher = Cipher(session.crypto.send_key)

        nonce = session.crypto.next_nonce()

        ciphertext = cipher.encrypt(
            nonce,
            plaintext,
        )

        return nonce + ciphertext

    @staticmethod
    def decrypt(session, payload: bytes):

        nonce = payload[:12]

        ciphertext = payload[12:]

        cipher = Cipher(session.crypto.receive_key)

        plaintext = cipher.decrypt(
            nonce,
            ciphertext,
        )

        return plaintext