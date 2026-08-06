import json
import time


class PongMessage:

    def __init__(self, timestamp=None):
        self.timestamp = timestamp or time.time()

    def encode(self):

        return json.dumps(
            {
                "timestamp": self.timestamp
            }
        ).encode()

    @classmethod
    def decode(cls, data):

        obj = json.loads(
            data.decode()
        )

        return cls(
            obj["timestamp"]
        )