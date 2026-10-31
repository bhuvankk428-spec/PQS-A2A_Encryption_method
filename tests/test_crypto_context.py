from agent.crypto.context import CryptoContext


def _load_pair():

    client = CryptoContext()

    server = CryptoContext()

    client.load_shared_secret(b"shared-secret", is_client=True)

    server.load_shared_secret(b"shared-secret", is_client=False)

    return client, server


def test_contexts_establish_matching_directional_keys():

    client, server = _load_pair()

    assert client.established is True

    assert server.established is True

    assert client.send_key == server.receive_key

    assert client.receive_key == server.send_key


def test_send_and_receive_keys_differ():

    client, _ = _load_pair()

    assert client.send_key != client.receive_key


def test_nonce_counter_increments():

    context = CryptoContext()

    assert context.next_nonce() == (0).to_bytes(12, "big")

    assert context.next_nonce() == (1).to_bytes(12, "big")


def test_reset_clears_keys():

    client, _ = _load_pair()

    client.reset()

    assert client.established is False

    assert client.shared_secret is None

    assert client.send_key is None

    assert client.receive_key is None
