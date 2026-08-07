import json
from agent.protocol.payloads.base import ProtocolMessage


class ReHandshakeMessage(ProtocolMessage):

    def __init__(self, reason="forward_secrecy"):
        self.reason = reason

    def encode(self):
        return json.dumps({
            "reason": self.reason
        }).encode()

    @classmethod
    def decode(cls, data):
        obj = json.loads(data.decode())
        return cls(obj["reason"])