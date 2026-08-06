import json
from pathlib import Path


CACHE_FILE = Path("session_cache.json")


class SessionCache:

    @staticmethod
    def save(
        session_id: str,
        shared_secret: bytes,
        key_version: int,
    ):

        data = {
            "session_id": session_id,
            "shared_secret": shared_secret.hex(),
            "key_version": key_version,
        }

        with open(
            CACHE_FILE,
            "w",
        ) as f:

            json.dump(data, f)

    @staticmethod
    def load():

        if not CACHE_FILE.exists():

            return None

        with open(
            CACHE_FILE,
            "r",
        ) as f:

            data = json.load(f)

        return {

            "session_id":
                data["session_id"],

            "shared_secret":
                bytes.fromhex(
                    data["shared_secret"]
                ),

            "key_version":
                data["key_version"],
        }

    @staticmethod
    def clear():

        if CACHE_FILE.exists():

            CACHE_FILE.unlink()