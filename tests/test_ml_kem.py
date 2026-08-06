from agent.crypto.ml_kem import MLKEM


print("========== CLIENT ==========")

client = MLKEM()

client_public = client.generate_keypair()

print("Public Key Size :", len(client_public))


print("\n========== SERVER ==========")

server = MLKEM()

ciphertext, server_secret = server.encapsulate(
    client_public
)

print("Ciphertext Size :", len(ciphertext))

print("Shared Secret Size :", len(server_secret))


print("\n========== CLIENT ==========")

client_secret = client.decapsulate(
    ciphertext
)

print("Shared Secret Size :", len(client_secret))


print("\n========== RESULT ==========")

print("Secrets Match :", client_secret == server_secret)