import time

from agent.session.manager import SessionManager
from agent.protocol.state import SessionState
from agent.security.forward_secrecy import ForwardSecrecy


def _established_session():
    manager = SessionManager()
    session = manager.create()
    session.set_state(SessionState.ESTABLISHED)
    return session


def test_no_rotation_when_idle():
    session = _established_session()
    assert ForwardSecrecy.should_rehandshake(session) is False


def test_rotation_after_message_interval():
    session = _established_session()
    session.crypto.messages_sent = ForwardSecrecy.ROTATION_INTERVAL
    assert ForwardSecrecy.should_rehandshake(session) is True


def test_rotation_after_timeout():
    session = _established_session()
    session.last_rehandshake = (
        time.time() - ForwardSecrecy.ROTATION_TIMEOUT - 1
    )
    assert ForwardSecrecy.should_rehandshake(session) is True


def test_no_rotation_while_rehandshaking():
    session = _established_session()
    session.rehandshaking = True
    session.crypto.messages_sent = (
        ForwardSecrecy.ROTATION_INTERVAL + 5
    )
    assert ForwardSecrecy.should_rehandshake(session) is False