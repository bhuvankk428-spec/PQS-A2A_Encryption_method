import uuid

from agent.protocol.packet import Packet
from agent.protocol.constants import HELLO

session = uuid.uuid4()

packet = Packet(
    packet_type=HELLO,
    session_id=session,
    sequence=1,
    payload=b"Hello Agent",
)

encoded = packet.encode()

decoded = Packet.decode(encoded)

print(decoded.version)
print(decoded.packet_type)
print(decoded.session_id)
print(decoded.sequence)
print(decoded.payload)