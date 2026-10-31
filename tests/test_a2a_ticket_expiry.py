import time

import pytest

from agent.config import MAJOR_KEY_LIFETIME
from agent.session.store import SessionStore
from agent.session.ticket import SessionTicket


def _ticket(age=0, expires_in=MAJOR_KEY_LIFETIME):

    return SessionTicket(
        session_id="session-1",
        shared_secret=b"\x02" * 32,
        created_at=time.time() - age,
        expires_in=expires_in,
    )


def test_major_key_lifetime_is_one_hour():

    assert MAJOR_KEY_LIFETIME == 60 * 60


@pytest.mark.parametrize(
    "age, expected",
    [
        (0, False),
        (MAJOR_KEY_LIFETIME - 1, False),
        (MAJOR_KEY_LIFETIME + 1, True),
        (MAJOR_KEY_LIFETIME * 2, True),
    ],
)
def test_ticket_expiry_boundary(age, expected):

    assert _ticket(age=age).expired() is expected


def test_store_rejects_expired_ticket():

    store = SessionStore()

    store.save(_ticket(age=MAJOR_KEY_LIFETIME + 1))

    assert store.get("session-1") is None

    assert "session-1" not in store.tickets


def test_store_returns_live_ticket():

    store = SessionStore()

    ticket = _ticket(age=MAJOR_KEY_LIFETIME - 1)

    store.save(ticket)

    assert store.get("session-1") is ticket
