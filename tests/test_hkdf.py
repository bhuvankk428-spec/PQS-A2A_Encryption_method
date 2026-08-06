from agent.crypto.ml_kem import MLKEM
from agent.crypto.hkdf import KeyDerivation


client = MLKEM()

server = MLKEM()

client_public = client.generate_keypair()

ciphertext, server_secret = server.encapsulate(
    client_public
)

client_secret = client.decapsulate(
    ciphertext
)

assert client_secret == server_secret

client_send, client_receive = KeyDerivation.derive(
    client_secret
)

server_send, server_receive = KeyDerivation.derive(
    server_secret
)

print("Shared Secret Equal :", client_secret == server_secret)

print()

print("Client Send Key :", client_send.hex())

print("Client Receive Key :", client_receive.hex())

print()

print("Server Send Key :", server_send.hex())

print("Server Receive Key :", server_receive.hex())

print()

print("Keys Equal :", client_send == server_send)