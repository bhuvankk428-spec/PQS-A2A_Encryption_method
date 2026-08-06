from pqcrypto.kem.ml_kem_768 import (
    generate_keypair,
    encrypt,
    decrypt,
)
from agent.crypto.kem import KEM
class MLKEM(KEM):

    def __init__(self):

        self.public_key = None
        self.private_key = None

    def generate_keypair(self):

        self.public_key, self.private_key = generate_keypair()
 
        print("Public Key Length :", len(self.public_key))
        print("Private Key Length:", len(self.private_key))

        return self.public_key

    def encapsulate(self, public_key):

        ciphertext, shared_secret = encrypt(public_key)

        return ciphertext, shared_secret

    def decapsulate(self, ciphertext):

      shared_secret = decrypt(
        self.private_key,
        ciphertext,
    )

      return shared_secret