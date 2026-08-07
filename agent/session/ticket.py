from dataclasses import dataclass, field
import time


@dataclass
class SessionTicket:

    session_id: str

    shared_secret: bytes

    key_version: int = 1

    created_at: float = field(default_factory=time.time)

    expires_in: int = 3600

    def expired(self):

        return (
            time.time()
            >
            self.created_at + self.expires_in
        )