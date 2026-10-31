from agent.crypto.ml_kem import MLKEM


def test_keypair_and_ciphertext_sizes():

    client = MLKEM()

    public_key = client.generate_keypair()

    server = MLKEM()

    ciphertext, shared_secret = server.encapsulate(public_key)

    assert len(public_key) == 1184

    assert len(client.private_key) == 2400

    assert len(ciphertext) == 1088

    assert len(shared_secret) == 32


def test_client_decapsulates_server_secret():

    client = MLKEM()

    server = MLKEM()

    public_key = client.generate_keypair()

    ciphertext, server_secret = server.encapsulate(public_key)

    assert client.decapsulate(ciphertext) == server_secret


def test_each_keypair_is_unique():

    first = MLKEM()

    second = MLKEM()

    assert first.generate_keypair() != second.generate_keypair()
