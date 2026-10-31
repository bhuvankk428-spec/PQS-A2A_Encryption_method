import pytest

from agent.crypto.cipher import Cipher
from agent.crypto.context import CryptoContext
from agent.crypto.ml_kem import MLKEM


def _handshake():

    client_kem = MLKEM()

    server_kem = MLKEM()

    public_key = client_kem.generate_keypair()

    ciphertext, server_secret = server_kem.encapsulate(public_key)

    client_secret = client_kem.decapsulate(ciphertext)

    assert client_secret == server_secret

    client = CryptoContext()

    server = CryptoContext()

    client.load_shared_secret(client_secret, is_client=True)

    server.load_shared_secret(server_secret, is_client=False)

    return client, server


@pytest.mark.parametrize(
    "message",
    [
        b"",
        b"hello agent",
        "quantum-safe \u00e9\u00e8".encode("utf-8"),
        b"A" * 8192,
    ],
    ids=["empty", "ascii", "utf8", "large"],
)
def test_client_to_server_round_trip(message):

    client, server = _handshake()

    nonce = client.next_nonce()

    ciphertext = Cipher(client.send_key).encrypt(nonce, message)

    assert Cipher(server.receive_key).decrypt(nonce, ciphertext) == message


def test_server_to_client_round_trip():

    client, server = _handshake()

    message = b"reply from agent B"

    nonce = server.next_nonce()

    ciphertext = Cipher(server.send_key).encrypt(nonce, message)

    assert Cipher(client.receive_key).decrypt(nonce, ciphertext) == message


def test_send_keys_are_directional():

    client, server = _handshake()

    assert client.send_key == server.receive_key

    assert client.receive_key == server.send_key

    assert client.send_key != server.send_key
