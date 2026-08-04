import struct


HEADER = "!BBII"

HEADER_SIZE = struct.calcsize(HEADER)


class Packet:

    def __init__(
        self,
        packet_type: int,
        sequence: int,
        payload: bytes,
    ):
        self.version = 1
        self.packet_type = packet_type
        self.sequence = sequence
        self.payload = payload

    def encode(self):

        header = struct.pack(
            HEADER,
            self.version,
            self.packet_type,
            self.sequence,
            len(self.payload),
        )

        return header + self.payload

    @classmethod
    def decode(cls, data: bytes):

        version, packet_type, sequence, length = struct.unpack(
            HEADER,
            data[:HEADER_SIZE],
        )

        payload = data[
            HEADER_SIZE:
            HEADER_SIZE + length
        ]

        return cls(
            packet_type,
            sequence,
            payload,
        )