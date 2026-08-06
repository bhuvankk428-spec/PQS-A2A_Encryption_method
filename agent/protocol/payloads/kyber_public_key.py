import json
import base64

from agent.protocol.payloads.base import ProtocolMessage


class KyberPublicKeyMessage(ProtocolMessage):

    def __init__(
        self,
        peer_id: str,
        public_key: bytes,
    ):

        self.peer_id = peer_id
        self.public_key = public_key

    def encode(self):

        return json.dumps({

            "peer_id": self.peer_id,

            "public_key":

            base64.b64encode(
                self.public_key
            ).decode()

        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(data.decode())

        return cls(

            obj["peer_id"],

            base64.b64decode(
                obj["public_key"]
            )

        )