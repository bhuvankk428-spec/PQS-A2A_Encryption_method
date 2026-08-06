import json

from agent.protocol.payloads.base import ProtocolMessage


class ErrorMessage(ProtocolMessage):

    def __init__(
        self,
        code: int,
        message: str,
    ):
        self.code = code
        self.message = message

    def encode(self):

        return json.dumps({

            "code": self.code,
            "message": self.message,

        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(
            data.decode()
        )

        return cls(
            obj["code"],
            obj["message"],
        )