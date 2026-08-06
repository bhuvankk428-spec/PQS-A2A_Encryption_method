from agent.protocol.handlers.base import PacketHandler
from agent.protocol.payloads.error import ErrorMessage


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