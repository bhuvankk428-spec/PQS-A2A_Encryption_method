from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class Cipher:

    def __init__(self, key: bytes):

        self.cipher = AESGCM(key)

    def encrypt(
        self,
        nonce: bytes,
        plaintext: bytes,
        aad: bytes = b"",
    ):

        ciphertext = self.cipher.encrypt(
            nonce,
            plaintext,
            aad,
        )

        return ciphertext

    def decrypt(
        self,
        nonce: bytes,
        ciphertext: bytes,
        aad: bytes = b"",
    ):

        plaintext = self.cipher.decrypt(
            nonce,
            ciphertext,
            aad,
        )

        return plaintext