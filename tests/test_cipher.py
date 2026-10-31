from agent.crypto.cipher import Cipher
from agent.crypto.hkdf import KeyDerivation
from agent.crypto.ml_kem import MLKEM


def test_ml_kem_shared_secret_agreement():

    client = MLKEM()

    server = MLKEM()

    public_key = client.generate_keypair()

    ciphertext, server_secret = server.encapsulate(public_key)

    client_secret = client.decapsulate(ciphertext)

    assert client_secret == server_secret


def test_hkdf_derives_two_distinct_256_bit_keys():

    send_key, receive_key = KeyDerivation.derive(b"shared-secret")

    assert len(send_key) == 32

    assert len(receive_key) == 32

    assert send_key != receive_key


def test_aes_gcm_round_trip():

    send_key, _ = KeyDerivation.derive(b"shared-secret")

    cipher = Cipher(send_key)

    nonce = (0).to_bytes(12, "big")

    message = b"Hello Secure World"

    encrypted = cipher.encrypt(nonce, message)

    assert len(encrypted) == len(message) + 16

    assert cipher.decrypt(nonce, encrypted) == message
