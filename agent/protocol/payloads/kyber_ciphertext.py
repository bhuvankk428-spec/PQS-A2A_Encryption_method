import json
import base64

from agent.protocol.payloads.base import ProtocolMessage
from agent.protocol.payloads.key_confirm import KeyConfirmMessage

class KyberCiphertextMessage(ProtocolMessage):

    def __init__(
        self,
        ciphertext: bytes,
    ):

        self.ciphertext = ciphertext

    def encode(self):

        return json.dumps({

            "ciphertext":

            base64.b64encode(
                self.ciphertext
            ).decode()

        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(data.decode())

        return cls(

            base64.b64decode(
                obj["ciphertext"]
            )

        )