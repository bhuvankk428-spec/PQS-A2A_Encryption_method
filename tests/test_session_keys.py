from agent.crypto.ml_kem import MLKEM
from agent.crypto.context import CryptoContext
from agent.crypto.cipher import Cipher


def _kex():
    """Simulate the ML-KEM-768 exchange between client and server."""
    client = MLKEM()
    server = MLKEM()

    public_key = client.generate_keypair()
    ciphertext, server_secret = server.encapsulate(public_key)
    client_secret = client.decapsulate(ciphertext)

    return client_secret, server_secret


def test_shared_secret_matches():
    client_secret, server_secret = _kex()
    assert client_secret == server_secret


def test_key_direction_swap():
    secret, _ = _kex()

    client = CryptoContext()
    server = CryptoContext()

    client.load_shared_secret(secret, is_client=True)
    server.load_shared_secret(secret, is_client=False)

    assert client.send_key == server.receive_key
    assert server.send_key == client.receive_key
    assert client.send_key != client.receive_key


def test_nonces_unique_within_epoch():
    secret, _ = _kex()

    ctx = CryptoContext()
    ctx.load_shared_secret(secret, is_client=True)

    nonces = {ctx.next_nonce() for _ in range(256)}

    assert len(nonces) == 256


def test_installing_new_keys_resets_nonce_epoch():
    secret, _ = _kex()

    ctx = CryptoContext()
    ctx.load_shared_secret(secret, is_client=True)
    ctx.next_nonce()

    # New key version -> new epoch, nonce counter restarts (safe because the
    # keys are fresh, so the (key, nonce) pair is not reused).
    ctx.load_shared_secret(secret, is_client=True, version=2)

    assert ctx.next_nonce() == (0).to_bytes(12, "big")


def test_resume_fresh_keys_regression():
    """Regression test.

    Previously a resumed session re-derived the SAME AES keys from the cached
    master secret and restarted the nonce counter at zero, causing AES-GCM
    (key, nonce) reuse. With a per-connection resume salt the keys must differ.
    """
    secret, _ = _kex()

    conn1 = CryptoContext()
    conn2 = CryptoContext()

    conn1.load_shared_secret(secret, is_client=True, salt=b"resume-salt-A", version=1)
    conn2.load_shared_secret(secret, is_client=True, salt=b"resume-salt-B", version=1)

    assert conn1.send_key != conn2.send_key
    assert conn1.receive_key != conn2.receive_key

    # Deterministic on both sides: identical salt reproduces identical keys.
    server = CryptoContext()
    server.load_shared_secret(secret, is_client=False, salt=b"resume-salt-A", version=1)

    assert server.receive_key == conn1.send_key
    assert server.send_key == conn1.receive_key


def test_aes_roundtrip():
    secret, _ = _kex()

    client = CryptoContext()
    server = CryptoContext()

    client.load_shared_secret(secret, is_client=True)
    server.load_shared_secret(secret, is_client=False)

    nonce = client.next_nonce()

    ciphertext = Cipher(client.send_key).encrypt(nonce, b"hello")

    plaintext = Cipher(server.receive_key).decrypt(nonce, ciphertext)

    assert plaintext == b"hello"