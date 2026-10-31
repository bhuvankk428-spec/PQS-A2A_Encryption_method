import uuid

from agent.session.manager import SessionManager
from agent.session.session import Session


def test_create_session_registers_it():

    manager = SessionManager()

    session = manager.create()

    assert isinstance(session, Session)

    assert manager.exists(session.session_id) is True

    assert manager.count() == 1


def test_get_or_create_returns_existing_instance():

    manager = SessionManager()

    session = manager.create()

    restored = manager.get_or_create(session.session_id)

    assert restored is session


def test_get_or_create_creates_missing_session():

    manager = SessionManager()

    session_id = uuid.uuid4()

    session = manager.get_or_create(session_id)

    assert session.session_id == session_id

    assert manager.count() == 1


def test_remove_session():

    manager = SessionManager()

    session = manager.create()

    manager.remove(session.session_id)

    assert manager.exists(session.session_id) is False

    assert manager.count() == 0
