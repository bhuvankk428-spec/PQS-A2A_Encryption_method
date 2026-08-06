from dataclasses import dataclass, field
from uuid import UUID
import time

from agent.protocol.state import SessionState
from agent.crypto.context import CryptoContext

@dataclass
class Session:

    session_id: UUID

    state: SessionState = field(default=SessionState.NEW)

    send_sequence: int = 1

    receive_sequence: int = 0

    active: bool = True

    crypto: CryptoContext = field(
    default_factory=CryptoContext
)

    created_at: float = field(default_factory=time.time)

    last_activity: float = field(default_factory=time.time)

    def next_send_sequence(self) -> int:

        sequence = self.send_sequence

        self.send_sequence += 1

        self.touch()

        return sequence

    def update_receive_sequence(self, sequence: int):

        if sequence > self.receive_sequence:
            self.receive_sequence = sequence

        self.touch()

    def touch(self):

        self.last_activity = time.time()

    def close(self):

        self.active = False

        self.touch()

    def set_state(self, state: SessionState):

        self.state = state

        self.touch()

    def is_established(self):

        return self.state == SessionState.ESTABLISHED