from agent.peer.peer import Peer


def test_peer_create_sets_defaults():

    peer = Peer.create("Agent-A")

    assert peer.name == "Agent-A"

    assert peer.version == "SPQ-A2A/1.0"

    assert peer.peer_id


def test_peer_ids_are_unique():

    assert Peer.create("Agent-A").peer_id != Peer.create("Agent-A").peer_id
