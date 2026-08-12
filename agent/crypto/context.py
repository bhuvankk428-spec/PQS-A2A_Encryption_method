from dataclasses import dataclass


@dataclass
class CryptoContext:
    # Message Counter
    messages_sent: int = 0
    messages_received: int = 0

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
        """Monotonic 12-byte nonce for the CURRENT key epoch.

        The counter is reset inside :meth:`install_keys`, which also installs
        a FRESH pair of AES keys, so the (key, nonce) pair is never repeated.
        """
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

        self.messages_sent = 0
        self.messages_received = 0

        self.nonce_counter = 0
        self.key_version = 1
        self.established = False

    def install_keys(
        self,
        key1: bytes,
        key2: bytes,
        is_client: bool,
    ):
        """Install a fresh pair of AES keys and start a new key epoch.

        The nonce counter and the message counters are reset here, so callers
        MUST only pass keys that are themselves fresh -- a new ML-KEM shared
        secret, a new rotation version, or keys derived with a fresh
        per-connection resume salt. Otherwise the (key, nonce) pair could be
        reused, which would totally break AES-GCM.
        """
        if is_client:
            self.send_key = key1
            self.receive_key = key2
        else:
            self.send_key = key2
            self.receive_key = key1

        self.messages_sent = 0
        self.messages_received = 0
        self.nonce_counter = 0
        self.established = True

    def load_shared_secret(
        self,
        shared_secret: bytes,
        is_client: bool,
        salt: bytes | None = None,
        version: int | None = None,
    ):
        """Derive AES session keys from a shared secret.

        ``salt`` is required for session resumption: deriving from the same
        long-lived master secret with a fresh random salt yields fresh AES
        keys per connection, preventing nonce reuse across resumed sessions.
        """
        from agent.crypto.hkdf import KeyDerivation

        self.shared_secret = shared_secret

        key_version = (
            self.key_version
            if version is None
            else version
        )

        key1, key2 = (
            KeyDerivation.derive_resume(
                shared_secret,
                salt,
                key_version,
            )
            if salt is not None
            else KeyDerivation.derive(
                shared_secret,
                key_version,
            )
        )

        self.key_version = key_version

        self.install_keys(
            key1,
            key2,
            is_client,
        )

    def sent(self):
        self.messages_sent += 1

    def received(self):
        self.messages_received += 1