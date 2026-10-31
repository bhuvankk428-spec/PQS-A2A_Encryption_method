import uuid

import pytest

from agent.protocol.constants import HELLO
from agent.protocol.packet import HEADER_SIZE, Packet


def test_packet_round_trip_preserves_fields():

    session_id = uuid.uuid4()

    packet = Packet(
        packet_type=HELLO,
        session_id=session_id,
        sequence=1,
        payload=b"Hello Agent",
    )

    encoded = packet.encode()

    decoded = Packet.decode(encoded)

    assert len(encoded) == HEADER_SIZE + len(b"Hello Agent")

    assert decoded.version == packet.version

    assert decoded.packet_type == HELLO

    assert decoded.session_id == session_id

    assert decoded.sequence == 1

    assert decoded.payload == b"Hello Agent"


@pytest.mark.parametrize("payload", [b"", b"x", b"A" * 4096])
def test_packet_payload_sizes(payload):

    packet = Packet(
        packet_type=HELLO,
        session_id=uuid.uuid4(),
        sequence=2,
        payload=payload,
    )

    assert Packet.decode(packet.encode()).payload == payload


def test_truncated_packet_rejected():

    with pytest.raises(ValueError, match="Packet too small"):

        Packet.decode(b"\x00")
