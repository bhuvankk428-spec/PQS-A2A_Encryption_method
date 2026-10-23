import json
import time
from pathlib import Path

from agent.config import MAJOR_KEY_LIFETIME


CACHE_FILE = Path("session_cache.json")


class SessionCache:

    @staticmethod
    def save(
        session_id: str,
        shared_secret: bytes,
        key_version: int,
        created_at: float | None = None,
        expires_in: int = MAJOR_KEY_LIFETIME,
    ):

        data = {
            "session_id": session_id,
            "shared_secret": shared_secret.hex(),
            "key_version": key_version,
            "created_at": created_at if created_at is not None else time.time(),
            "expires_in": expires_in,
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

        try:
            with open(
                CACHE_FILE,
                "r",
            ) as f:

                data = json.load(f)

        except (OSError, json.JSONDecodeError):

            SessionCache.clear()

            return None

        created_at = data.get("created_at")
        expires_in = data.get("expires_in", MAJOR_KEY_LIFETIME)

        # Caches written before expiry tracking are not trusted
        if (
            created_at is None
            or time.time() > created_at + expires_in
        ):
            SessionCache.clear()

            return None

        try:
            return {

                "session_id":
                    data["session_id"],

                "shared_secret":
                    bytes.fromhex(
                        data["shared_secret"]
                    ),

                "key_version":
                    data["key_version"],

                "created_at":
                    created_at,
            }

        except (KeyError, TypeError, ValueError):

            SessionCache.clear()

            return None

    @staticmethod
    def clear():

        if CACHE_FILE.exists():

            CACHE_FILE.unlink()