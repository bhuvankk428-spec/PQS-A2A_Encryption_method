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
        print("\n========== ENCODE ==========")
        print("Packet Type :", self.packet_type)
        print("Payload Length:", len(self.payload))
        print("Total Length :", len(header + self.payload))
        print("============================")
        return header + self.payload

    @classmethod
    def decode(cls, data: bytes):

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

        payload = data[
            HEADER_SIZE:
            HEADER_SIZE + payload_length
        ]
        print("\n========== DECODE ==========")
        print("Raw Bytes            :", len(data))
        print("Payload Length(Header):", payload_length)
        print("Payload Length(Actual):", len(payload))
        print("============================")
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