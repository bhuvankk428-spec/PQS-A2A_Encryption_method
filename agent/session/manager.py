import uuid
from uuid import UUID

from agent.session.session import Session


class SessionManager:

    def __init__(self):

        self.sessions = {}

    def create(self, session_id: UUID | None = None):

        if session_id is None:
            session_id = uuid.uuid4()

        session = Session(session_id=session_id)

        self.sessions[session.session_id] = session

        return session

    def get(self, session_id: UUID):

        return self.sessions.get(session_id)

    def exists(self, session_id: UUID):

        return session_id in self.sessions

    def remove(self, session_id: UUID):

        self.sessions.pop(session_id, None)

    def count(self):

        return len(self.sessions)

    def get_or_create(self, session_id: UUID):

        if self.exists(session_id):
            return self.get(session_id)

        return self.create(session_id)