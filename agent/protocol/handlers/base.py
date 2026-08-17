from abc import ABC, abstractmethod


class PacketHandler(ABC):

    @abstractmethod
    def handle(
        self,
        session,
        packet,
    ):
        pass