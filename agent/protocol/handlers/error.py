from agent.protocol.handlers.base import PacketHandler
from agent.protocol.payloads.error import ErrorMessage
from monitor.events import protocol_event
class ErrorHandler(PacketHandler):

    def handle(self, session, packet):

        error = ErrorMessage.decode(
            packet.payload
        )

        print()

        print("========== ERROR ==========")
        print("Code   :", error.code)
        print("Reason :", error.message)
        print("===========================")

        return None