import struct
import uuid

from agent.protocol.constants import PROTOCOL_VERSION

HEADER_FORMAT = "!BBBB16sII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


class Packet:

    def __init__(
        self,
        packet_type: int,
        session_id: uuid.UUID,
        sequence: int,
        payload: bytes,
        flags: int = 0,
    ):
        self.version = PROTOCOL_VERSION
        self.packet_type = packet_type
        self.flags = flags
        self.reserved = 0
        self.session_id = session_id
        self.sequence = sequence
        self.payload = payload

    def encode(self):

        header = struct.pack(
            HEADER_FORMAT,
            self.version,
            self.packet_type,
            self.flags,
            self.reserved,
            self.session_id.bytes,
            self.sequence,
            len(self.payload),
        )

        return header + self.payload

    @classmethod
    def decode(cls, data: bytes):

        if len(data) < HEADER_SIZE:
            raise ValueError("Packet too small")

        (
            version,
            packet_type,
            flags,
            reserved,
            session_bytes,
            sequence,
            payload_length,
        ) = struct.unpack(
            HEADER_FORMAT,
            data[:HEADER_SIZE],
        )

        if version != PROTOCOL_VERSION:
            raise ValueError(
                "Unsupported protocol version"
            )

        if payload_length < 0:
            raise ValueError(
                "Invalid payload length"
            )

        if HEADER_SIZE + payload_length > len(data):
            raise ValueError(
                "Packet truncated"
            )

        payload = data[
            HEADER_SIZE:
            HEADER_SIZE + payload_length
        ]

        packet = cls(
            packet_type,
            uuid.UUID(bytes=session_bytes),
            sequence,
            payload,
            flags,
        )

        packet.version = version
        packet.reserved = reserved

        return packet