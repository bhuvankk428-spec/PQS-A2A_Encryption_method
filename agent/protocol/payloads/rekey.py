import json

from agent.protocol.payloads.base import ProtocolMessage


class RekeyMessage(ProtocolMessage):

    def __init__(

        self,

        key_version: int,

        acknowledge: bool = False,

    ):

        self.key_version = key_version

        self.acknowledge = acknowledge

    def encode(self):

        return json.dumps({

            "key_version": self.key_version,

            "ack": self.acknowledge,

        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(

            data.decode()

        )

        return cls(

            obj["key_version"],

            obj["ack"],

        )