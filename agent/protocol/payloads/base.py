from abc import ABC, abstractmethod


class ProtocolMessage(ABC):

    @abstractmethod
    def encode(self) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def decode(cls, data: bytes):
        pass