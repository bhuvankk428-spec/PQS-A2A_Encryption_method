import os

HOST = "localhost"

PORT = 4433

MINI_KEY_LIFETIME = int(
    os.getenv("MINI_KEY_LIFETIME", 6 * 60)
)

MINI_KEY_MESSAGE_LIMIT = int(
    os.getenv("MINI_KEY_MESSAGE_LIMIT", 10)
)

MAJOR_KEY_LIFETIME = int(
    os.getenv("MAJOR_KEY_LIFETIME", 60 * 60)
)

PROTOCOL_VERSION = 1

AGENT_NAME = "Agent-A"