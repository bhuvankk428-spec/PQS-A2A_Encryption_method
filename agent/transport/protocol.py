from aioquic.asyncio.protocol import QuicConnectionProtocol


class AgentProtocol(QuicConnectionProtocol):

    def connection_made(self, transport):
        super().connection_made(transport)
        print("[QUIC] Connection Established")

    def connection_lost(self, exc):
        print("[QUIC] Connection Closed")
        super().connection_lost(exc)