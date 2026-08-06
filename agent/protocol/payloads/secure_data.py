import json
import base64

from agent.protocol.payloads.base import ProtocolMessage


class SecureDataMessage(ProtocolMessage):

    def __init__(
        self,
        data: bytes,
    ):

        self.data = data

    def encode(self):

        return json.dumps({

            "data":

            base64.b64encode(
                self.data
            ).decode()

        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(data.decode())

        return cls(

            base64.b64decode(
                obj["data"]
            )

        )