from agent.crypto.hkdf import KeyDerivation


def test_derive_is_deterministic():

    assert KeyDerivation.derive(b"shared-secret") == KeyDerivation.derive(
        b"shared-secret"
    )


def test_directional_keys_are_unique():

    send_key, receive_key = KeyDerivation.derive(b"shared-secret")

    assert send_key != receive_key

    assert len(send_key) == 32

    assert len(receive_key) == 32


def test_key_version_changes_derived_keys():

    version_one = KeyDerivation.derive(b"shared-secret", version=1)

    version_two = KeyDerivation.derive(b"shared-secret", version=2)

    assert version_one != version_two
