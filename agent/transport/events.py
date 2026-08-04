from enum import Enum


class Event(Enum):

    CONNECTED = "CONNECTED"

    DISCONNECTED = "DISCONNECTED"

    PACKET_RECEIVED = "PACKET_RECEIVED"