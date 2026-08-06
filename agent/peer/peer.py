from dataclasses import dataclass
import uuid


@dataclass
class Peer:

    peer_id: str
    name: str
    version: str = "SPQ-A2A/1.0"

    @classmethod
    def create(cls, name: str):

        return cls(
            peer_id=str(uuid.uuid4()),
            name=name,
        )