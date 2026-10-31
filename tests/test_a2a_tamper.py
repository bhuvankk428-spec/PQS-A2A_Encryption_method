import pytest
from cryptography.exceptions import InvalidTag

from agent.crypto.cipher import Cipher
from agent.crypto.context import CryptoContext


def _pair():

    client = CryptoContext()

    server = CryptoContext()

    shared_secret = b"\x01" * 32

    client.load_shared_secret(shared_secret, is_client=True)

    server.load_shared_secret(shared_secret, is_client=False)

    return client, server


@pytest.mark.parametrize("index", [0, 5, -1])
def test_flipped_ciphertext_bit_fails_aes_gcm(index):

    client, server = _pair()

    nonce = client.next_nonce()

    ciphertext = bytearray(
        Cipher(client.send_key).encrypt(nonce, b"secret message")
    )

    ciphertext[index] ^= 0x01

    with pytest.raises(InvalidTag):

        Cipher(server.receive_key).decrypt(nonce, bytes(ciphertext))


def test_truncated_ciphertext_fails_aes_gcm():

    client, server = _pair()

    nonce = client.next_nonce()

    ciphertext = Cipher(client.send_key).encrypt(nonce, b"secret message")

    with pytest.raises(InvalidTag):

        Cipher(server.receive_key).decrypt(nonce, ciphertext[:-1])


def test_wrong_aad_fails_aes_gcm():

    client, server = _pair()

    nonce = client.next_nonce()

    ciphertext = Cipher(client.send_key).encrypt(
        nonce,
        b"secret message",
        aad=b"header",
    )

    with pytest.raises(InvalidTag):

        Cipher(server.receive_key).decrypt(
            nonce,
            ciphertext,
            aad=b"wrong-header",
        )
