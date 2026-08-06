from agent.crypto.ml_kem import MLKEM
from agent.crypto.hkdf import KeyDerivation
from agent.crypto.cipher import Cipher

# ---------------- ML-KEM ----------------

client = MLKEM()
server = MLKEM()

public_key = client.generate_keypair()

ciphertext, server_secret = server.encapsulate(public_key)

client_secret = client.decapsulate(ciphertext)

assert client_secret == server_secret

# ---------------- HKDF ----------------

send_key, receive_key = KeyDerivation.derive(client_secret)

# ---------------- AES ----------------

cipher = Cipher(send_key)

# Fixed nonce (ONLY FOR TESTING)
nonce = (0).to_bytes(12, "big")

message = b"Hello Secure World"

encrypted = cipher.encrypt(
    nonce,
    message,
)

print("Ciphertext Length:", len(encrypted))

decrypted = cipher.decrypt(
    nonce,
    encrypted,
)

print("Decrypted:", decrypted.decode())
print("Match:", decrypted == message)