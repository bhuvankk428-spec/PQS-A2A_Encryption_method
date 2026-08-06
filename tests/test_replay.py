from agent.security.replay import ReplayWindow


def test_first_packet():

    replay = ReplayWindow()

    assert replay.validate(1) is True

    print("✓ First packet accepted")


def test_duplicate_packet():

    replay = ReplayWindow()

    replay.validate(1)

    assert replay.validate(1) is False

    print("✓ Duplicate packet rejected")


def test_increasing_sequence():

    replay = ReplayWindow()

    for i in range(1, 11):

        assert replay.validate(i) is True

    print("✓ Increasing sequence accepted")


def test_old_packet():

    replay = ReplayWindow()

    # Fill replay window
    for i in range(1, 100):

        replay.validate(i)

    # Packet outside replay window
    assert replay.validate(1) is False

    print("✓ Old packet rejected")


def test_window_slide():

    replay = ReplayWindow()

    for i in range(1, 70):

        replay.validate(i)

    # Duplicate within window
    assert replay.validate(69) is False

    # Very old packet
    assert replay.validate(1) is False

    # New packet
    assert replay.validate(70) is True

    print("✓ Sliding window works")


if __name__ == "__main__":

    print("\n===== Replay Protection Tests =====\n")

    test_first_packet()

    test_duplicate_packet()

    test_increasing_sequence()

    test_old_packet()

    test_window_slide()

    print("\n✓ All Replay Protection Tests Passed")