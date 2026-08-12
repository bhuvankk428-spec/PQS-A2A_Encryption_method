import time


class Metrics:

    def __init__(self):
        self.connections = 0

        self.handshakes = 0

        self.resume_success = 0
        self.resume_failed = 0

        self.packets_sent = 0
        self.packets_received = 0

        self.bytes_sent = 0
        self.bytes_received = 0

        self.encrypted_messages = 0
        self.decrypted_messages = 0

        self.rekeys = 0
        self.replay_attacks = 0

        self.pings = 0
        self.pongs = 0

        self.handshake_start = None
        self.handshake_times = []

    def start_handshake(self):
        self.handshake_start = time.perf_counter()

    def finish_handshake(self):
        if self.handshake_start is not None:
            elapsed = time.perf_counter() - self.handshake_start
            self.handshake_times.append(elapsed)
            self.handshake_start = None

    def average_handshake(self):
        if not self.handshake_times:
            return 0
        return sum(self.handshake_times) / len(self.handshake_times)

    def print(self):
        print()
        print("========== METRICS ==========")

        print(f"Connections        : {self.connections}")
        print(f"Handshakes         : {self.handshakes}")

        print(f"Resume Success     : {self.resume_success}")
        print(f"Resume Failed      : {self.resume_failed}")

        print(f"Packets Sent       : {self.packets_sent}")
        print(f"Packets Received   : {self.packets_received}")

        print(f"Bytes Sent         : {self.bytes_sent}")
        print(f"Bytes Received     : {self.bytes_received}")

        print(f"Encrypted Messages : {self.encrypted_messages}")
        print(f"Decrypted Messages : {self.decrypted_messages}")

        print(f"Replay Attacks     : {self.replay_attacks}")

        print(f"Rekeys             : {self.rekeys}")

        print(f"Pings              : {self.pings}")
        print(f"Pongs              : {self.pongs}")

        print(
            f"Average Handshake  : "
            f"{self.average_handshake():.3f} sec"
        )

        print("=============================")

    def to_dict(self):
        return {
            "connections": self.connections,
            "handshakes": self.handshakes,
            "resume_success": self.resume_success,
            "resume_failed": self.resume_failed,
            "packets_sent": self.packets_sent,
            "packets_received": self.packets_received,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "encrypted_messages": self.encrypted_messages,
            "decrypted_messages": self.decrypted_messages,
            "rekeys": self.rekeys,
            "replay_attacks": self.replay_attacks,
            "pings": self.pings,
            "pongs": self.pongs,
            "average_handshake": round(self.average_handshake(), 4),
        }

    # ---------- Helper Methods ----------

    def packet_sent(self, size):
        self.packets_sent += 1
        self.bytes_sent += size

    def packet_received(self, size):
        self.packets_received += 1
        self.bytes_received += size

    def encrypted(self):
        self.encrypted_messages += 1

    def decrypted(self):
        self.decrypted_messages += 1

    def replay_attack(self):
        self.replay_attacks += 1

    def ping(self):
        self.pings += 1

    def pong(self):
        self.pongs += 1

    def resume_successful(self):
        self.resume_success += 1

    def resume_failed_event(self):
        self.resume_failed += 1

    def rekey(self):
        self.rekeys += 1


metrics = Metrics()