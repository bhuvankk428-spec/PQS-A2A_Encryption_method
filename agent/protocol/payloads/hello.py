import json

from agent.protocol.payloads.base import ProtocolMessage


class HelloMessage(ProtocolMessage):

    def __init__(self, peer_id, name, version):

        self.peer_id = peer_id
        self.name = name
        self.version = version

    def encode(self):

        return json.dumps({

            "peer_id": self.peer_id,

            "name": self.name,

            "version": self.version

        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(data.decode())

        return cls(

            obj["peer_id"],

            obj["name"],

            obj["version"]

        )