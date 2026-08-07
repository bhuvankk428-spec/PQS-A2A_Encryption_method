from abc import ABC, abstractmethod
from monitor.server import emit_log
from monitor.events import protocol_event
class PacketHandler(ABC):

    @abstractmethod
    def handle(
        self,
        session,
        packet,
    ):
        pass