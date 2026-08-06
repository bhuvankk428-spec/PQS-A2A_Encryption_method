import json

from agent.protocol.payloads.base import ProtocolMessage


class KeyConfirmMessage(ProtocolMessage):

    def __init__(self, success: bool = True):
        self.success = success

    def encode(self):

        return json.dumps({
            "success": self.success
        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(data.decode())

        return cls(
            success=obj["success"]
        )