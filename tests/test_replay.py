import pytest

from agent.security.replay import ReplayWindow


def test_first_packet():

    replay = ReplayWindow()

    assert replay.validate(1) is True


def test_duplicate_packet():

    replay = ReplayWindow()

    assert replay.validate(1) is True

    assert replay.validate(1) is False


def test_increasing_sequence():

    replay = ReplayWindow()

    for i in range(1, 11):

        assert replay.validate(i) is True


def test_old_packet():

    replay = ReplayWindow()

    for i in range(1, 100):

        replay.validate(i)

    assert replay.validate(1) is False


def test_window_slide():

    replay = ReplayWindow()

    for i in range(1, 70):

        replay.validate(i)

    assert replay.validate(69) is False

    assert replay.validate(1) is False

    assert replay.validate(70) is True


@pytest.mark.parametrize(
    "highest, sequence, expected",
    [
        (64, 0, True),      # exactly 64 apart: still inside the window
        (65, 0, False),     # 65 apart: outside the window
        (100, 36, True),    # exactly 64 apart
        (100, 35, False),   # 65 apart
    ],
)
def test_window_boundary(highest, sequence, expected):

    replay = ReplayWindow()

    assert replay.validate(highest) is True

    assert replay.validate(sequence) is expected


def test_out_of_order_arrival():

    replay = ReplayWindow()

    assert replay.validate(10) is True

    assert replay.validate(5) is True

    assert replay.validate(7) is True

    assert replay.validate(8) is True

    assert replay.validate(7) is False

    assert replay.validate(6) is True

    assert replay.validate(11) is True


def test_zero_sequence_first_packet():

    replay = ReplayWindow()

    assert replay.validate(0) is True


def test_zero_sequence_duplicate_rejected():

    replay = ReplayWindow()

    assert replay.validate(0) is True

    assert replay.validate(0) is False


def test_zero_sequence_within_window():

    replay = ReplayWindow()

    assert replay.validate(64) is True

    assert replay.validate(0) is True
