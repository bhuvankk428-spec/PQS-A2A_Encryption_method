from dataclasses import dataclass
import time


@dataclass
class SessionTicket:

    session_id: str

    shared_secret: bytes

    created_at: float = time.time()

    expires_in: int = 3600

    def expired(self):

        return (
            time.time()
            >
            self.created_at
            + self.expires_in
        )