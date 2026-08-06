class ReplayWindow:

    WINDOW_SIZE = 64

    def __init__(self):

        self.highest_sequence = 0

        self.received = set()

    def validate(self, sequence: int) -> bool:

        # First packet
        if self.highest_sequence == 0:

            self.highest_sequence = sequence

            self.received.add(sequence)

            return True

        # Duplicate packet
        if sequence in self.received:

            return False

        # Too old
        if sequence < self.highest_sequence - self.WINDOW_SIZE:

            return False

        # New highest
        if sequence > self.highest_sequence:

            self.highest_sequence = sequence

        self.received.add(sequence)

        # Remove old entries
        self.received = {

            s

            for s in self.received

            if s >= self.highest_sequence - self.WINDOW_SIZE

        }

        return True