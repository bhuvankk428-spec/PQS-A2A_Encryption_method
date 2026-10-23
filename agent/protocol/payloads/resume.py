import json

from agent.protocol.payloads.base import ProtocolMessage


class ResumeMessage(ProtocolMessage):

    def __init__(

        self,

        session_id: str,

        success: bool = True,

    ):

        self.session_id = session_id

        self.success = success

    def encode(self):

        return json.dumps({

            "session_id":
            self.session_id,

            "success":
            self.success,

        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(
            data.decode()
        )

        return cls(
            obj["session_id"],
            obj.get("success", True),
        )