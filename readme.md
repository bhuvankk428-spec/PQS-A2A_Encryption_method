# Quantum Secure AI-to-AI Communication Protocol

## Overview

This project implements a **Quantum-Secure AI-to-AI Communication
Protocol** that enables autonomous AI agents to communicate securely
over QUIC using post-quantum cryptography.

The protocol combines:

-   QUIC Transport
-   ML-KEM (CRYSTALS-Kyber)
-   HKDF Key Derivation
-   AES-256-GCM Encryption
-   Secure Session Management
-   Session Resumption
-   Forward Secrecy
-   Autonomous AI-to-AI Communication

The system demonstrates how future AI systems can securely exchange
information even in the presence of quantum computers.

------------------------------------------------------------------------

## Features

-   QUIC-based secure transport
-   Post-Quantum Key Exchange (ML-KEM / Kyber)
-   AES-256-GCM encrypted communication
-   HKDF session key derivation
-   Session establishment and resumption
-   Forward secrecy support
-   Replay attack protection
-   Ping/Pong heartbeat mechanism
-   Autonomous AI Agent communication using OpenAI
-   Modular protocol architecture
-   Runtime metrics collection

------------------------------------------------------------------------

## Architecture

``` text
AI Agent A
    │
OpenAI Model
    │
Protocol Engine
    │
AES-256-GCM
    │
QUIC Transport
══════════════════════════════
 Secure Channel
══════════════════════════════
QUIC Transport
    │
AES-256-GCM
    │
Protocol Engine
    │
OpenAI Model
    │
AI Agent B
```

------------------------------------------------------------------------

## Cryptography

  Algorithm        Purpose
  ---------------- ---------------------------
  ML-KEM (Kyber)   Post-Quantum Key Exchange
  HKDF-SHA256      Session Key Derivation
  AES-256-GCM      Payload Encryption
  QUIC             Secure Transport

------------------------------------------------------------------------

## Protocol Flow

``` text
HELLO
   ↓
KYBER_PUBLIC_KEY
   ↓
KYBER_CIPHERTEXT
   ↓
KEY_CONFIRM
   ↓
Encrypted DATA
   ↓
PING / PONG
   ↓
Key-Pair Rotation (fresh Kyber handshake, repeating)
   ↓
Session Close
```

------------------------------------------------------------------------

## Running

``` bash
# 1. Install dependencies (pqcrypto/ML-KEM, OpenAI, socket.io)
venv\Scripts\python -m pip install -r requirements.txt

# 2. Generate a self-signed transport certificate (git-ignored - never commit
#    a private key). Only required on a fresh clone.
venv\Scripts\python certs\generate_certs.py

# 3. Terminal 1 - QUIC server (also relays events to the dashboard socket)
venv\Scripts\python agent\transport\server.py

# 4. Terminal 2 - QUIC client (run twice to exercise session resumption)
venv\Scripts\python agent\transport\client.py

# 5. Tests
venv\Scripts\python -m pytest
```

### Dashboard (React + Socket.IO)

The QUIC server automatically starts the monitor backend
(`monitor/server.py`) on **http://localhost:5000**, which serves the built
dashboard and streams live protocol events.

``` bash
# 1. Install dashboard dependencies
npm --prefix dashboard install

# 2. Development mode (HMR) - run `npm --prefix dashboard run dev` and open
#    the printed URL. It talks to the backend on localhost:5000.
npm --prefix dashboard run dev

# 3. Production: build the SPA (output to dashboard/dist), then simply visit
#    http://localhost:5000 while the QUIC server is running.
npm --prefix dashboard run build
```

The socket endpoint is `http://localhost:5000`; override it with the
`VITE_SOCKET_URL` environment variable if the dashboard is served elsewhere.

------------------------------------------------------------------------

## Post-Quantum Security Model

-   **Transport**: aioquic (QUIC + TLS 1.3). All QUIC packet payloads and
    header metadata are encrypted by TLS, giving multiplexed streams,
    connection reuse/migration, and resistance to passive eavesdropping,
    replay, downgrade, session-hijacking and traffic analysis.
-   **Key exchange**: ML-KEM-768 (CRYSTALS-Kyber) via the NIST `pqcrypto`
    bindings, replacing the classically-vulnerable ECDH that Shor's
    algorithm would break.
-   **Data encryption**: AES-256-GCM with fresh per-connection session keys
    derived through HKDF-SHA384.
-   **Frequent key-pair rotation**: every `ROTATION_INTERVAL` encrypted
    messages (or `ROTATION_TIMEOUT` seconds) the peers run a fresh ML-KEM
    key-pair handshake and discard the old shared secret. This limits the
    exposure window to residual Module-LWE / side-channel risk of a single
    Kyber key-pair and provides post-quantum forward secrecy. Implemented by
    the `REHANDSHAKE` path (`agent/security/forward_secrecy.py`).
-   **Session resumption**: the long-lived master secret may be cached, but
    AES session keys are always re-derived with a fresh random resume salt,
    so key + nonce pairs are never reused across connections (nonce reuse
    would catastrophically break AES-GCM).
-   **Replay protection**: per-session sliding-window sequence validation.
-   **Note**: ML-KEM is an unauthenticated key-encapsulation mechanism; the
    demo does not authenticate the peer. Production use must add a
    signature/ML-DSA or a mutually-authenticated TLS layer.

------------------------------------------------------------------------

## Project Structure

``` text
agent/
├── ai/
├── crypto/
├── metrics/
├── peer/
├── protocol/
│   ├── handlers/
│   ├── payloads/
│   ├── engine.py
│   ├── packet.py
│   └── messages.py
├── security/
├── session/
├── transport/
├── client.py
└── server.py
```

------------------------------------------------------------------------

## Example AI Conversation

``` text
Agent A: Greetings, fellow AI.
Agent B: Excellent, let's synchronize protocols.
Agent A: Agreed, initiating secure communication.
Agent B: All systems remain secure.
```

------------------------------------------------------------------------

## Runtime Metrics

The protocol records:

-   Connections
-   Handshake Time
-   Packets Sent
-   Packets Received
-   Encrypted Messages
-   Session Resume Count
-   Replay Attacks
-   Rekey Operations
-   Ping/Pong RTT

------------------------------------------------------------------------

## Technologies

-   Python 3.13
-   aioquic
-   OpenAI API
-   ML-KEM (Kyber)
-   AES-256-GCM
-   HKDF
-   AsyncIO

------------------------------------------------------------------------

## Future Enhancements

-   Interactive Web Dashboard
-   Live Packet Visualization
-   Multi-Agent Communication
-   Digital Signatures
-   Distributed AI Network
-   Performance Analytics

------------------------------------------------------------------------

## License

MIT License
   8th aug last working commit
   by Bhuvan