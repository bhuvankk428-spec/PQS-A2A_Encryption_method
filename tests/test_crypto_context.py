from agent.session.manager import SessionManager
from agent.crypto.ml_kem import MLKEM

manager = SessionManager()

session = manager.create()

client = MLKEM()
server = MLKEM()

client_public = client.generate_keypair()

ciphertext, server_secret = server.encapsulate(client_public)

client_secret = client.decapsulate(ciphertext)

session.crypto.load_shared_secret(client_secret, is_client=True)

print("Established :", session.crypto.established)

print("Shared Secret :", len(session.crypto.shared_secret))

print("Send Key :", len(session.crypto.send_key))

print("Receive Key :", len(session.crypto.receive_key))