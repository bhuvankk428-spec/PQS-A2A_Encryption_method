import json

from agent.protocol.payloads.base import ProtocolMessage


class HelloAckMessage(ProtocolMessage):

    def __init__(
        self,
        peer_id: str,
        accepted: bool,
    ):

        self.peer_id = peer_id
        self.accepted = accepted

    def encode(self):

        return json.dumps({

            "peer_id": self.peer_id,
            "accepted": self.accepted

        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(data.decode())

        return cls(
            obj["peer_id"],
            obj["accepted"],
        )