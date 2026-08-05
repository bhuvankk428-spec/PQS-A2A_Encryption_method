
import asyncio
import ssl
import uuid

from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

from agent.transport.protocol import AgentProtocol
from agent.protocol.packet import Packet
from agent.protocol.constants import HELLO

async def main():

    configuration = QuicConfiguration(
        is_client=True
    )

    configuration.verify_mode = ssl.CERT_NONE

    async with connect(
        "127.0.0.1",
        4433,
        configuration=configuration,
        create_protocol=AgentProtocol,
    ) as protocol:

        print("[CLIENT] Connected")

        reader, writer = await protocol.create_stream()
        session = uuid.uuid4()
        packet = Packet(
    packet_type=HELLO,
    session_id=session,
    sequence=1,
    payload=b"HELLO AGENT",
)

        writer.write(packet.encode())

        await writer.drain()

        data = await reader.read(4096)

        reply = Packet.decode(data)

        print("\n========== ACK RECEIVED ==========")
        print("Version    :", reply.version)
        print("Type       :", reply.packet_type)
        print("Session ID :", reply.session_id)
        print("Sequence   :", reply.sequence)
        print("Payload    :", reply.payload.decode())
        print("==================================")

        writer.close()

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())