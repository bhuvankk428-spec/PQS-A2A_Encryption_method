from dataclasses import dataclass


@dataclass
class CryptoContext:

    # ML-KEM
    public_key: bytes | None = None
    private_key: bytes | None = None
    shared_secret: bytes | None = None
    ciphertext: bytes | None = None

    # AES Keys
    send_key: bytes | None = None
    receive_key: bytes | None = None

    # Nonce
    nonce_counter: int = 0

    # Key Rotation
    key_version: int = 1

    # Session Status
    established: bool = False

    def next_nonce(self) -> bytes:

        nonce = self.nonce_counter.to_bytes(12, "big")

        self.nonce_counter += 1

        return nonce

    def establish(self):

        self.established = True

    def reset(self):

        self.public_key = None
        self.private_key = None
        self.shared_secret = None
        self.ciphertext = None
        self.send_key = None
        self.receive_key = None
        self.nonce_counter = 0
        self.key_version = 1
        self.established = False

    def load_shared_secret(
        self,
        shared_secret: bytes,
        is_client: bool,
    ):

        from agent.crypto.hkdf import KeyDerivation

        self.shared_secret = shared_secret

        key1, key2 = KeyDerivation.derive(
            shared_secret
        )

        if is_client:

            self.send_key = key1
            self.receive_key = key2

        else:

            self.send_key = key2
            self.receive_key = key1

        self.established = True