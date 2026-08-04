import asyncio

from aioquic.asyncio import serve
from aioquic.quic.configuration import QuicConfiguration

from agent.transport.protocol import AgentProtocol


async def handle_stream(reader, writer):

    print("[SERVER] Stream Opened")

    while True:

        data = await reader.read(4096)

        if not data:
            break

        print("[SERVER] Received:", data.decode())

        writer.write(b"ACK")

        await writer.drain()

    writer.close()

    print("[SERVER] Stream Closed")


def stream_handler(reader, writer):
    asyncio.create_task(handle_stream(reader, writer))


async def main():

    configuration = QuicConfiguration(
        is_client=False
    )

    configuration.load_cert_chain(
        "certs/cert.pem",
        "certs/key.pem",
    )

    await serve(
        host="0.0.0.0",
        port=4433,
        configuration=configuration,
        create_protocol=AgentProtocol,
        stream_handler=stream_handler,
    )

    print("Agent A Listening on UDP 4433")

    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())