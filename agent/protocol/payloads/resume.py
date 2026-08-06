import json

from agent.protocol.payloads.base import ProtocolMessage


class ResumeMessage(ProtocolMessage):

    def __init__(

        self,

        session_id: str,

    ):

        self.session_id = session_id

    def encode(self):

        return json.dumps({

            "session_id":
            self.session_id

        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(
            data.decode()
        )

        return cls(
            obj["session_id"]
        )