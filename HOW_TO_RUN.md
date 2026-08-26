# How to Run This Project — Step-by-Step Guide

This project has **4 components** that must run simultaneously:
1. **Monitor Server** (Flask + Socket.IO) — relays protocol events to the dashboard
2. **Protocol Server** (Agent B) — QUIC server handling post-quantum handshake
3. **Protocol Client** (Agent A) — QUIC client that initiates the secure conversation
4. **React Dashboard** — live visualization of the protocol in action

---

## Prerequisites

Before running, make sure you have:
- **Python 3.13** installed
- **Node.js 18+** and **npm** installed
- **OpenAI API key** (the project uses `gpt-4.1-nano` model)
- **TLS certificates** in `certs/cert.pem` and `certs/key.pem` (already present in the repo)

---

## Step 1: Set Up Python Virtual Environment

Open a terminal in the project root (`D:\major_project`) and run:

```powershell
# Create virtual environment (if not already created)
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

---

## Step 2: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

**Important:** The `pqcrypto` library (used for ML-KEM-768 post-quantum cryptography) is **not listed** in `requirements.txt` but is required by the code. Install it separately:

```powershell
pip install pqcrypto
```

If `pqcrypto` fails to install (it requires C compilation), you may need:
- A C compiler (Visual Studio Build Tools on Windows, or `gcc` on Linux)
- CMake
- Python development headers

Alternative: install from the vendored `liboqs` library in the project if available.

---

## Step 3: Verify Environment Variables

The project needs an OpenAI API key. Check that `.env` exists in the project root:

```
OPENAI_API_KEY=sk-proj-...
```

If the file is missing or you need a new key, create `D:\major_project\.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

The key is loaded automatically by `python-dotenv` in `agent/ai/model.py`.

---

## Step 4: Verify TLS Certificates

The QUIC transport requires TLS certificates. Check that these files exist:

```
D:\major_project\certs\cert.pem
D:\major_project\certs\key.pem
```

If they are missing, regenerate them:

```powershell
# Create certs directory if needed
mkdir certs

# Generate self-signed certificate for localhost
openssl req -x509 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/CN=localhost"
```

---

## Step 5: Start the Monitor Server (Terminal 1)

The monitor server must be started **first** because the protocol handlers emit events to it.

```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Start the monitor server
python -m monitor.server
```

You should see output indicating Flask-SocketIO is running on `http://0.0.0.0:5000`.

---

## Step 6: Start the Protocol Server (Terminal 2)

Open a **new terminal**, activate the venv, and start the server:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Start the protocol server (Agent B)
python -m agent.transport.server
```

You should see output like:

```
Agent A Listening on UDP 4433
```

The server is now waiting for incoming QUIC connections on port 4433.

---

## Step 7: Start the Protocol Client (Terminal 3)

Open a **third terminal**, activate the venv, and start the client:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Start the protocol client (Agent A)
python -m agent.transport.client
```

The client will:
1. Connect to `localhost:4433` via QUIC
2. Perform the ML-KEM-768 post-quantum key exchange handshake
3. Establish an AES-256-GCM encrypted session
4. Generate AI messages via OpenAI and exchange 5 encrypted rounds
5. Send PING heartbeats every 5 seconds

You will see detailed logs of the handshake and encrypted conversation in the terminal.

**Optional:** To test session resumption, run the resume client instead:

```powershell
python -m agent.transport.client_resume
```

This client reuses a cached session from `session_cache.json` instead of performing a full handshake.

---

## Step 8: Start the React Dashboard (Terminal 4)

Open a **fourth terminal** and set up the frontend:

```powershell
# Navigate to the dashboard directory
cd dashboard

# Install dependencies (first time only)
npm install

# Start the Vite dev server
npm run dev
```

The dashboard will start on `http://localhost:5173` (default Vite port).

Open your browser and go to `http://localhost:5173`. You will see:
- **Live Log** — color-coded stream of all protocol events
- **Handshake Timeline** — visual step-by-step progress (HELLO -> KYBER_PUBLIC_KEY -> KYBER_CIPHERTEXT -> KEY_CONFIRM)
- **Packet Flow** — animated visualization of packets between Agent A and Agent B
- **Encryption Viewer** — shows Plaintext -> AES-256-GCM -> Ciphertext -> Decrypt -> Recovered
- **Agent Cards** — status of each AI agent
- **Metric Cards** — counters for packets, encrypted messages, rekeys, resumes

---

## Complete Startup Sequence (All Commands)

Open **4 separate terminals** and run these in order:

**Terminal 1 — Monitor Server:**
```powershell
cd D:\major_project
.\venv\Scripts\Activate.ps1
python -m monitor.server
```

**Terminal 2 — Protocol Server:**
```powershell
cd D:\major_project
.\venv\Scripts\Activate.ps1
python -m agent.transport.server
```

**Terminal 3 — Protocol Client:**
```powershell
cd D:\major_project
.\venv\Scripts\Activate.ps1
python -m agent.transport.client
```

**Terminal 4 — React Dashboard:**
```powershell
cd D:\major_project\dashboard
npm install   # first time only
npm run dev
```

---

## Running Tests

The project has manual test scripts in `tests/`. Run them from the project root:

```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Run individual test scripts
python tests/test_ml_kem.py        # ML-KEM key encapsulation
python tests/test_hkdf.py          # HKDF key derivation
python tests/test_cipher.py        # Full crypto pipeline (ML-KEM + HKDF + AES)
python tests/test_packet.py        # Packet encode/decode
python tests/test_crypto_context.py # CryptoContext + session integration
python tests/test_peer.py          # Peer creation
python tests/tes_session.py        # Session manager (note: filename typo)

# Run pytest-compatible tests (only test_replay.py has proper test functions)
pytest tests/test_replay.py -v
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pqcrypto'"
The `pqcrypto` package is not in `requirements.txt`. Install it manually:
```powershell
pip install pqcrypto
```

### "FileNotFoundError: certs/cert.pem"
TLS certificates are missing. Regenerate them:
```powershell
openssl req -x509 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes -subj "/CN=localhost"
```

### "Connection refused" on port 4433
Make sure the protocol server is running in Terminal 2 **before** starting the client in Terminal 3.

### Dashboard shows no events
Make sure the monitor server is running in Terminal 1. The protocol handlers only emit events if the monitor server is available. Also check that the dashboard is connecting to `http://localhost:5000` (check `dashboard/src/services/socket.js`).

### OpenAI API errors
Verify your `.env` file has a valid `OPENAI_API_KEY`. The project uses `gpt-4.1-nano` — make sure your API key has access to this model.

### Port already in use
If port 5000 or 4433 is already in use, find and kill the process:
```powershell
# Find process using a port
netstat -ano | findstr :5000
netstat -ano | findstr :4433

# Kill it by PID
taskkill /PID <PID> /F
```

### Dashboard build errors
Try clearing node_modules and reinstalling:
```powershell
cd dashboard
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json
npm install
npm run dev
```

---

## Architecture Quick Reference

| Component | Technology | Port | Command |
|---|---|---|---|
| Monitor Server | Flask + Socket.IO | 5000 (HTTP/WS) | `python -m monitor.server` |
| Protocol Server | Python + aioquic (QUIC/UDP) | 4433 (UDP) | `python -m agent.transport.server` |
| Protocol Client | Python + aioquic (QUIC/UDP) | — | `python -m agent.transport.client` |
| React Dashboard | Vite + React 19 | 5173 (HTTP) | `cd dashboard && npm run dev` |

---

## What Happens When You Run

1. The monitor server starts and begins listening for protocol events on port 5000.
2. The protocol server starts and listens for QUIC connections on UDP port 4433.
3. The protocol client connects to the server and sends a HELLO message.
4. The server responds with an ML-KEM-768 public key (post-quantum key exchange).
5. The client encapsulates a ciphertext and derives AES-256-GCM keys via HKDF-SHA384.
6. The server decapsulates the ciphertext, derives matching AES keys, and confirms the key exchange.
7. The session is now established with post-quantum security.
8. The client generates an AI message using OpenAI (`gpt-4.1-nano`), encrypts it, and sends it.
9. The server decrypts the message, generates an AI reply, encrypts it, and sends it back.
10. This encrypted conversation continues for 5 rounds.
11. Throughout, all protocol events are broadcast to the dashboard via the monitor server.
12. The React dashboard renders live visualizations of the handshake, encryption, packet flow, and metrics.
13. Every 5 seconds, the client sends a PING heartbeat and the server responds with PONG.
14. After 10 messages, forward secrecy triggers a fresh re-handshake with new keys.
