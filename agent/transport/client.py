import asyncio
import ssl

from aioquic.asyncio import connect

from aioquic.quic.configuration import QuicConfiguration

from agent.transport.protocol import AgentProtocol


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

        writer.write(b"HELLO AGENT")

        await writer.drain()

        data = await reader.read(4096)

        print("[CLIENT] Reply:", data.decode())

        writer.close()

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())