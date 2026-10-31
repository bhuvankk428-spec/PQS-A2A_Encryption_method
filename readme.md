# SPQ-A2A - Quantum-Secure AI-to-AI Communication over QUIC

[![tests](https://github.com/bhuvankk428-spec/PQS-A2A_Encryption_method/actions/workflows/test.yml/badge.svg)](https://github.com/bhuvankk428-spec/PQS-A2A_Encryption_method/actions/workflows/test.yml)

A working research prototype where two autonomous AI agents (Agent A and Agent B) talk to each
other over a QUIC/UDP channel. The application-layer handshake uses **ML-KEM-768** for
post-quantum key establishment, **HKDF-SHA384** for key derivation, and **AES-256-GCM** for
message encryption. A Flask/Socket.IO monitor relays protocol events to a React dashboard that
visualises the handshake, packets, encryption, key rotation, and live conversation.

> This is a demonstration/research prototype, not a production-hardened security product.
> Read [Security model](#security-model) and [Known limitations](#known-limitations) before
> deploying or presenting it as production security. A full incident list is in
> [PROBLEMS_FACED.txt](PROBLEMS_FACED.txt).

---

## Overview

| Item | Value |
|---|---|
| Project | Quantum-Secure AI-to-AI Communication Protocol (SPQ-A2A) |
| Transport | QUIC over UDP via `aioquic` |
| Post-quantum KEM | ML-KEM-768 (CRYSTALS-Kyber, NIST FIPS 203) via `pqcrypto` |
| Key derivation | HKDF-SHA384 (`cryptography`) |
| Symmetric cipher | AES-256-GCM (`cryptography`) |
| AI backend | OpenAI Chat Completions (`gpt-5.6-luna` by default, configurable) |
| Monitor | Flask + Flask-SocketIO on port 5000 |
| Dashboard | React 19 + Vite 8 + Tailwind + Socket.IO client |
| Runtime | Python 3.13, Node.js 18+ |
| Default ports | QUIC/UDP `4433`, monitor HTTP/WS `5000`, dashboard `5173` |

---

## What the demo does

1. Agent A (client) opens a QUIC connection to Agent B (server).
2. The agents perform a custom ML-KEM-768 handshake inside a QUIC bidirectional stream.
3. Both sides derive matching AES-256-GCM send/receive keys with HKDF-SHA384.
4. Agent A asks the OpenAI API for an opening line, encrypts it, and sends it as `DATA`.
5. Agent B decrypts it, asks OpenAI for a reply, encrypts the reply, and sends it back.
6. The conversation continues until the client process is stopped.
7. Every 5 seconds Agent A sends `PING`; Agent B answers with `PONG`.
8. Every 6 minutes or 10 encrypted sends (whichever comes first), Agent A rotates the
   "mini" AES key with a `REKEY`/`REKEY_ACK` exchange.
9. After 60 minutes, Agent A triggers a full ML-KEM `REHANDSHAKE` to replace the "major" key.
10. Every protocol step is relayed to the monitor and streamed to the React dashboard.

---

## Features

- QUIC transport with a 4-byte length-prefixed message framing layer.
- Custom binary protocol packet header (28 bytes) plus JSON payloads with base64 binary fields.
- ML-KEM-768 key encapsulation and decapsulation.
- HKDF-SHA384 derivation of directional 256-bit send/receive keys.
- AES-256-GCM authenticated encryption with a 96-bit counter nonce.
- Full handshake: `HELLO -> KYBER_PUBLIC_KEY -> KYBER_CIPHERTEXT -> KEY_CONFIRM`.
- Encrypted `DATA`, `PING`/`PONG`, `ERROR`, `REKEY`, `REHANDSHAKE`, and `RESUME` messages.
- Key lifecycle: major key (60 min) and mini key (6 min or 10 messages).
- Session resumption with a file cache and server-side in-memory tickets (1-hour TTL).
- Replay protection using a 64-packet sliding window (server side).
- Live monitor/dashboard: log stream, handshake timeline, packet flow, encryption viewer,
  agent cards, and metric cards.
- Modular handler-per-message-type protocol engine.

---

## Architecture

```
+---------------------------+          QUIC / UDP 4433          +---------------------------+
|      Agent A (client)     | <===============================> |      Agent B (server)     |
|                           |                                   |                           |
|  OpenAI model             |                                   |  OpenAI model             |
|  ProtocolEngine           |                                   |  ProtocolEngine           |
|  CryptoEngine             |                                   |  CryptoEngine             |
|    AES-256-GCM            |                                   |    AES-256-GCM            |
|    HKDF-SHA384            |                                   |    HKDF-SHA384            |
|    ML-KEM-768             |                                   |    ML-KEM-768             |
|  Session / Replay /       |                                   |  Session / Replay /       |
|  Rotation / Resume        |                                   |  Rotation / Resume        |
+-------------+-------------+                                   +-------------+-------------+
              |                                                               |
              |  protocol_event() -> HTTP POST /api/emit                      |
              v                                                               v
+---------------------------------------------------------------------------------------------+
|                  Monitor server: Flask + Flask-SocketIO, port 5000                          |
|                  Broadcasts "protocol_event" over Socket.IO                                 |
+---------------------------------------------------------------------------------------------+
                                        |
                                        v
+---------------------------------------------------------------------------------------------+
|                  React dashboard: http://localhost:5173                                    |
|   LiveLog | HandshakeTimeline | PacketFlow | EncryptionViewer | MetricCards | AgentCards    |
+---------------------------------------------------------------------------------------------+
```

### Components

| Directory / component | Responsibility |
|---|---|
| `agent/transport/` | QUIC client/server, stream framing, packet send/receive |
| `agent/protocol/` | Message types, state machine, packet encoding, handlers, payloads |
| `agent/crypto/` | ML-KEM wrapper, HKDF, AES-GCM cipher, crypto context |
| `agent/security/` | Replay window, mini-key rotation, major-key rehandshake trigger |
| `agent/session/` | Session objects, manager, ticket store, resume cache |
| `agent/ai/` | OpenAI wrapper with timeout and fallback |
| `agent/metrics/` | In-process metrics collector |
| `monitor/` | Flask-SocketIO event relay (`/api/emit` -> `protocol_event`) |
| `dashboard/` | React/Vite live visualisation |
| `tests/` | Pytest suite: crypto, protocol, replay window, A2A key exchange, tampering, ticket expiry |
| `doc/` | Research notes, FIPS 203 paper, data-flow documentation |
| `liboqs/` | Vendored liboqs source tree (not used by the running Python code) |

---

## Protocol flow

### Full handshake

```
Agent A                                                          Agent B
   |                                                                |
   |  HELLO (peer id, name, version) ------------------------------> |
   |                                                                |  generate ML-KEM-768 keypair
   |  <------------------------------ KYBER_PUBLIC_KEY (1184 B pk)  |
   |  encapsulate -> ciphertext + shared secret                     |
   |  HKDF-SHA384(shared secret) -> AES send/receive keys           |
   |  KYBER_CIPHERTEXT (1088 B ct) --------------------------------> |
   |                                                                |  decapsulate
   |                                                                |  HKDF -> matching AES keys
   |  <--------------------------------------- KEY_CONFIRM (true)   |
   |  ESTABLISHED                                                   |  ESTABLISHED
   |  <----------------- encrypted DATA (AES-256-GCM) -------------> |
```

### Wire format

Each message is sent as:

```
+----------------------+-------------------------------+----------------------+
| 4-byte big-endian    | 28-byte binary packet header  | JSON payload         |
| payload length       | version, type, flags, rsvd,   | (base64 for binary  |
|                      | session UUID, seq, payload len| key/ciphertext data) |
+----------------------+-------------------------------+----------------------+
```

The header format used by `agent/protocol/packet.py` is `!BBBB16sII`.
Payload fields such as ML-KEM keys, ciphertexts, and nonces are base64-encoded inside JSON.

### Key lifecycle

| Key | Scope | Created | Rotated / expires |
|---|---|---|---|
| QUIC TLS certificate | Transport (`certs/cert.pem`, `certs/key.pem`) | Static file | Not rotated by this app |
| Major key (ML-KEM shared secret) | Whole session | Handshake or resume | Full `REHANDSHAKE` after `MAJOR_KEY_LIFETIME` (default 3600 s); ticket/cache TTL also 1 h |
| Mini key (AES-256-GCM) | Current key epoch | Handshake, resume, or `REKEY` | `REKEY` after `MINI_KEY_MESSAGE_LIMIT` encrypted sends (10) or `MINI_KEY_LIFETIME` seconds (360), whichever comes first |
| Nonce | Per `CryptoContext` | Counter starting at 0 | Not persisted across resume (see limitations) |

Rotation is checked from the client heartbeat and at safe points in the data loop. The client
initiates a `REKEY` only when no reply is in flight and no rehandshake is pending.

### Session resumption

On startup the client looks for `session_cache.json`. If a valid, unexpired cache exists it sends
`RESUME` instead of `HELLO`. The server validates the session ticket from its in-memory
`SessionStore`; the ticket TTL is 1 hour. On failure the server now sends an explicit negative
`RESUME` response, the client clears the cache, and falls back to a full handshake. The client
also times out a silent `RESUME` after 10 seconds.

---

## Security model

Implemented:

- **Post-quantum key establishment:** ML-KEM-768 instead of classical ECDH.
- **Confidentiality and integrity:** AES-256-GCM (AEAD) for application messages.
- **Key separation:** HKDF-SHA384 derives independent send/receive keys; the server swaps them.
- **Replay protection:** 64-packet sliding window on the server.
- **Key rotation:** periodic mini-key rekey and periodic full ML-KEM rehandshake.
- **Session resumption:** cached shared secret and in-memory server ticket with expiry.
- **Authentication of the transport:** QUIC uses TLS certificates.

Important caveats:

- The client sets `verify_mode = ssl.CERT_NONE`, so the demo does **not** verify the server
  certificate. In this configuration a man-in-the-middle is possible unless certificate
  verification is enabled and certificates are managed properly.
- ML-KEM is an unauthenticated KEM. The application layer does not add digital signatures or
  agent identity verification; authentication relies on the TLS layer.
- The mini-key rotation is HKDF re-derivation from the same ML-KEM shared secret. It changes the
  AES key but is not independent forward secrecy. Only the major-key rehandshake creates a new
  shared secret.
- `session_cache.json` stores the shared secret on disk and does not persist nonce counters.
  Do not use resumption as-is in production (see [Known limitations](#known-limitations)).

---

## Project structure

```
major_project/
  agent/
    ai/                  OpenAI wrapper
    crypto/              ML-KEM, HKDF, AES-GCM, CryptoContext
    metrics/             metrics collector
    peer/                peer identity
    protocol/            packet, state, engine, handlers, payloads
    security/            replay, rotation, forward secrecy
    session/             session, manager, store, ticket, cache
    transport/           QUIC client, resume client, server, framing
    config.py            host/port and key-lifetime configuration
  monitor/
    events.py            protocol_event() HTTP relay
    server.py            Flask-SocketIO monitor
  dashboard/
    src/                 React components, hooks, socket client
  tests/                 crypto/protocol tests
  certs/                 self-signed TLS certificate and key
  doc/                   papers, research notes, detailed data flow
  liboqs/                vendored liboqs source (reference only)
  ARCHITECTURE_AND_DATA_FLOW.md
  HOW_TO_RUN.md
  PROBLEMS_FACED.txt     problem log and resolutions
  requirements.txt
```

---

## Requirements

- Python 3.13 (3.11+ should work but is not tested)
- Node.js 18+ and npm
- An OpenAI API key with access to the configured model
- TLS certificate files in `certs/` (present in the repo)
- C toolchain only if `pqcrypto` has no prebuilt wheel for your platform

### Dependency note

`requirements.txt` lists every Python dependency needed to run the full system, including the
previously missing runtime packages:

```text
openai==2.30.0          # AI conversation
pqcrypto==0.4.0         # ML-KEM-768
Flask==2.3.3            # monitor server
Flask-SocketIO==5.6.1   # monitor WebSocket relay
```

It also pins their transitive dependencies (for example `httpx`, `pydantic`, `python-socketio`,
`python-engineio`) so a fresh virtual environment is reproducible. Install everything with:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Setup

### 1. Python environment

```powershell
cd D:\major_project
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Environment variables

Create `.env` in the project root:

```env
OPENAI_API_KEY=your_key_here
# Optional:
# OPENAI_MODEL=gpt-5.6-luna
# MAJOR_KEY_LIFETIME=3600
# MINI_KEY_LIFETIME=360
# MINI_KEY_MESSAGE_LIMIT=10
```

`.env` is gitignored. Never commit real keys.

### 3. Certificates

The repository contains `certs/cert.pem` and `certs/key.pem`. To regenerate them:

```powershell
openssl req -x509 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem `
  -days 365 -nodes -subj "/CN=localhost"
```

### 4. Dashboard dependencies

```powershell
cd dashboard
npm install
```

---

## Running

Open four terminals in the project root. Activate the Python virtual environment in the three
Python terminals.

### Terminal 1 - monitor server

```powershell
.\venv\Scripts\Activate.ps1
python -m monitor.server
```

Starts Flask-SocketIO at `http://0.0.0.0:5000`.

### Terminal 2 - protocol server (Agent B)

```powershell
.\venv\Scripts\Activate.ps1
python -m agent.transport.server
```

Listens for QUIC on UDP `4433` and loads the certificate chain from `certs/`.

### Terminal 3 - protocol client (Agent A)

```powershell
.\venv\Scripts\Activate.ps1
python -m agent.transport.client
```

Performs the handshake (or resumes a cached session), then starts the encrypted AI conversation.
Stop it with `Ctrl+C`.

### Terminal 4 - React dashboard

```powershell
cd dashboard
npm run dev
```

Open `http://localhost:5173`.

### Optional - resume-only client

```powershell
.\venv\Scripts\Activate.ps1
python -m agent.transport.client_resume
```

This client always attempts `RESUME` first and falls back to a full handshake if rejected.

### Startup order

1. Monitor server (so events can be received).
2. Protocol server.
3. Dashboard (or start it at any time).
4. Protocol client.

---

## Configuration

| Setting | Default | Where | Meaning |
|---|---|---|---|
| `HOST` | `localhost` | `agent/config.py` | Logical host value |
| `PORT` | `4433` | `agent/config.py`, `agent/transport/server.py` | QUIC UDP port |
| `MAJOR_KEY_LIFETIME` | `3600` s | env / `agent/config.py` | ML-KEM key + ticket + cache lifetime |
| `MINI_KEY_LIFETIME` | `360` s | env / `agent/config.py` | Mini AES key lifetime |
| `MINI_KEY_MESSAGE_LIMIT` | `10` | env / `agent/config.py` | Encrypted sends before mini rekey |
| `OPENAI_MODEL` | `gpt-5.6-luna` | env / `agent/ai/model.py` | OpenAI model name |
| `OPENAI_API_KEY` | none | `.env` | OpenAI credential |
| MONITOR_URL | `http://localhost:5000/api/emit` | `monitor/events.py` | Event relay endpoint |
| Dashboard socket URL | `http://localhost:5000` | `dashboard/src/services/socket.js` | Socket.IO server |
| Replay window | 64 sequences | `agent/security/replay.py` | Replay acceptance window |
| Heartbeat interval | 5 s | `agent/transport/client.py` | PING interval |
| OpenAI timeout | 20 s, 1 retry | `agent/ai/model.py` | Prevents long stalls |

To demo rotation quickly:

```powershell
$env:MINI_KEY_MESSAGE_LIMIT = "3"
$env:MINI_KEY_LIFETIME = "60"
$env:MAJOR_KEY_LIFETIME = "90"
```

Start the server and client from shells that share these environment variables.

---

## Tests

Run the full pytest suite from the project root:

```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

The suite currently contains 55 tests and covers ML-KEM, HKDF, AES-GCM, packet encoding, sessions,
replay-window edge cases
(out-of-order arrival, the 64-packet boundary, sequence 0), A2A key-exchange round trips,
tampered ciphertext rejection, and 1-hour session-ticket expiry.

GitHub Actions runs the same command on every push and pull request via
[`.github/workflows/test.yml`](.github/workflows/test.yml).

Because `tests/` becomes the import root when pytest is invoked from inside that directory, always
run pytest from the project root.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'agent'` | Pytest run from inside `tests/` | Run `python -m pytest` from the project root |
| `ModuleNotFoundError: pqcrypto` / `openai` / `flask` | Virtual environment not synced with `requirements.txt` | Activate the venv and run `pip install -r requirements.txt` |
| OpenAI `404 model not found` | Model retired or unavailable to the key | Set `OPENAI_MODEL` to a model your key can access |
| Client prints `[AI ERROR]` and sends `Hello.` | API error, timeout, missing key, or unavailable model | Check `.env`, network, model access |
| Client hangs or freezes after a few messages | Resume failure, decryption mismatch, or an earlier long OpenAI call | Clear `session_cache.json`, restart server and client, check both consoles; updated code has 10 s resume timeout, 20 s AI timeout, and decrypt-failure rehandshake |
| Resume always fails after restarting the server | Server tickets are in memory only | Expected; let the client fall back to a full handshake or clear the cache |
| Dashboard shows nothing | Monitor is not running, or no events are arriving | Start `python -m monitor.server` first; verify `POST /api/emit` returns `{"ok":true}`; check port 5000 |
| Rehandshake not visible | 10-message/6-minute trigger is a mini `REKEY`, not a full rehandshake | Set `MAJOR_KEY_LIFETIME=60` for a quick visual demo |
| Port already in use | Old monitor/server process | `netstat -ano | findstr :5000` / `:4433`, then `taskkill /PID <pid> /F` |
| Duplicate server processes during automation | `Start-Process`/`Start-Job` spawning extra children | Kill stale `python.exe` processes by command line; start one server manually |
| Garbled characters in docs/console | UTF-8 text displayed with a legacy code page | Use a UTF-8 terminal/editor; source files are UTF-8 |
| Dashboard lint/build errors | ESLint rules about unused React imports or fast-refresh exports | Run `npm run lint` and `npm run build`; current code passes both |

---

## Known limitations

These are intentionally called out so the demo is not mistaken for production security:

1. **No certificate verification** in the client (`ssl.CERT_NONE`).
2. **No application-layer signatures or agent authentication.** ML-KEM alone does not authenticate
   the peer.
3. **Static TLS certificates.** Certificates are files in `certs/`, not per-user or per-session
   credentials. The 1-hour lifetime applies to the application's major key/ticket, not the TLS
   certificate.
4. **Mini-key rotation is HKDF re-derivation from the same shared secret**, so it is not
   independent forward secrecy.
5. **Session resumption does not persist nonce counters.** Restoring the same key with a fresh
   counter can cause AES-GCM nonce reuse. Disable resumption or persist/reject old nonces before
   production use.
6. **`session_cache.json` stores the shared secret in plaintext on disk.**
7. **Server tickets are in memory only**, so a server restart invalidates resumption.
8. **Replay protection is server-side only**; the client does not validate incoming replay
   windows.
9. **Dashboard metrics are derived from live events** and reset when the page reloads; there is no
   backend metrics API.
10. **The protocol engine swallows handler exceptions** (prints and returns `None`), which can
    appear as a silent stall.
11. **OpenAI is a hard runtime dependency** for conversation content; it is not needed for the
    cryptographic handshake itself.
12. **The conversation loop runs until stopped**; there is no five-message cap anymore. Token
    limits per response remain (`max_completion_tokens=80`).
13. **Vendored `liboqs` is not wired into the Python path**; the code uses the `pqcrypto` package.

See [PROBLEMS_FACED.txt](PROBLEMS_FACED.txt) for the history of these issues, including root
causes and what was changed.

---

## Documentation

- [HOW_TO_RUN.md](HOW_TO_RUN.md) - detailed step-by-step run guide
- [ARCHITECTURE_AND_DATA_FLOW.md](ARCHITECTURE_AND_DATA_FLOW.md) - architecture and data flow
- [doc/DATA_FLOW_DETAILED.md](doc/DATA_FLOW_DETAILED.md) - deep dive with diagrams
- [doc/key_poinst.md](doc/key_poinst.md) - research talking points on QUIC, TLS 1.3, ML-KEM
- [doc/summary_bhuvan.txt](doc/summary_bhuvan.txt) - research summary
- [PROBLEMS_FACED.txt](PROBLEMS_FACED.txt) - problem log and fixes
- [doc/NIST.FIPS.203.pdf](doc/NIST.FIPS.203.pdf) - ML-KEM standard

---

## License

MIT License. See [doc/LICENSE](doc/LICENSE).

Originally started by Bhuvan. The project has since been extended with key rotation, resumption,
monitor relay, dashboard fixes, and documentation updates.
