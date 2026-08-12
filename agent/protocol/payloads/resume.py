import json
import secrets

from agent.protocol.payloads.base import ProtocolMessage


class ResumeMessage(ProtocolMessage):

    def __init__(
        self,
        session_id: str,
        resume_salt: str | None = None,
    ):

        self.session_id = session_id
        # Fresh random salt -> fresh per-connection AES keys on resume.
        self.resume_salt = resume_salt or secrets.token_hex(16)

    def encode(self):

        return json.dumps({
            "session_id": self.session_id,
            "resume_salt": self.resume_salt,
        }).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(
            data.decode()
        )

        return cls(
            obj["session_id"],
            obj.get("resume_salt"),
        )