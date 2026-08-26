# System Architecture and Data Flow

## Project Overview

This project implements a **Quantum-Secure AI-to-AI Communication Protocol** — a client-server system where two autonomous AI agents (Agent A and Agent B) communicate over a secure channel using post-quantum cryptography, QUIC transport, and AES-256-GCM symmetric encryption. The system has three major subsystems: a Python backend for the core protocol engine, a Flask+Socket.IO monitor server for real-time event relay, and a React frontend dashboard for live visualization.

---

## System Architecture

### High-Level Architecture

The system is composed of three interconnected layers. At the core sits the **Protocol Engine** (Python) which handles all cryptographic operations, session management, and AI agent communication over QUIC/UDP. Layered on top is the **Monitor Server** (Flask + Socket.IO) which collects protocol events in real time and broadcasts them via WebSockets. The outermost layer is the **React Dashboard** which consumes WebSocket events and renders live visualizations of the handshake, encryption pipeline, packet flow, and metrics.

```
+----------------------------+         QUIC/UDP (port 4433)         +----------------------------+
|      CLIENT (Agent A)      | ==================================> |      SERVER (Agent B)      |
|                            |                                     |                            |
|  AIModel (OpenAI GPT)      |                                     |  AIModel (OpenAI GPT)      |
|       |                    |                                     |       |                    |
|  CryptoEngine              |                                     |  CryptoEngine              |
|    AES-256-GCM encrypt     |                                     |    AES-256-GCM decrypt     |
|       |                    |                                     |       |                    |
|  ML-KEM-768 (pqcrypto)     |                                     |  ML-KEM-768 (pqcrypto)     |
|    Key Encapsulation       |                                     |    Key Decapsulation       |
|       |                    |                                     |       |                    |
|  HKDF-SHA384               |                                     |  HKDF-SHA384               |
|    Key Derivation          |                                     |    Key Derivation          |
|       |                    |                                     |       |                    |
|  SessionManager            |                                     |  SessionManager            |
|  SessionCache (file)       |                                     |  SessionStore (memory)     |
|  ReplayWindow              |                                     |  ReplayWindow              |
|  ForwardSecrecy            |                                     |  ForwardSecrecy            |
|  KeyRotation               |                                     |  KeyRotation               |
|       |                    |                                     |       |                    |
|  Metrics (singleton)       |                                     |  Metrics (singleton)       |
+----------------------------+                                     +----------------------------+
          |                                                                   |
          |   protocol_event()                                                |
          v                                                                   v
+-------------------------------------------------------------------------------------------+
|                          Flask-SocketIO Monitor Server (port 5000)                         |
|                          monitor/server.py + monitor/events.py                              |
+-------------------------------------------------------------------------------------------+
          |                                                                   |
          |  WebSocket (socket.io) "protocol_event"                          |
          v                                                                   v
+-------------------------------------------------------------------------------------------+
|                           React Dashboard (Vite + React 19)                                |
|                                                                                           |
|   useProtocol hook ----> LiveLog | HandshakeTimeline | PacketFlow | EncryptionViewer      |
|   MetricCards <---------+--------+------------------+---------------+                      |
|   AgentCards  <---------+--------+------------------+---------------+                      |
+-------------------------------------------------------------------------------------------+
```

---

## Module Breakdown

### 1. Python Backend (`agent/`)

The backend is the core protocol engine. It is organized into the following modules:

- **transport/** — Manages QUIC connections over UDP using `aioquic`. The server listens on port 4433 and the client connects to localhost. Packet framing uses a 4-byte big-endian length prefix. The client also supports session resume via cached session tickets.
- **protocol/** — Defines the custom protocol state machine with message types (HELLO, KYBER_PUBLIC_KEY, KYBER_CIPHERTEXT, KEY_CONFIRM, DATA, REHANDSHAKE, REKEY, RESUME, PING, PONG, ERROR), packet encoding/decoding with a 24-byte binary header, and session state transitions.
- **protocol/handlers/** — One handler per message type. Each handler processes incoming packets, performs cryptographic operations, updates session state, emits monitoring events, and returns response packets.
- **protocol/payloads/** — JSON-serializable message classes for each protocol message type, handling serialization and deserialization of fields like keys, ciphertexts, and nonces (base64-encoded for binary data).
- **crypto/** — Implements ML-KEM-768 (CRYSTALS-Kyber) post-quantum key encapsulation, AES-256-GCM symmetric encryption/decryption, HKDF-SHA384 key derivation, and a `CryptoContext` dataclass that holds all cryptographic state for a session.
- **session/** — Manages session lifecycle including in-memory session storage, file-based session caching for resumption, server-side session tickets with expiry (TTL: 1 hour), and session state tracking.
- **security/** — Provides replay protection via a sliding window of 64 sequence numbers, forward secrecy by triggering re-handshake every 10 messages, and key rotation by re-deriving AES keys using HKDF with version-bumped labels.
- **ai/** — Wraps the OpenAI API (model: `gpt-4.1-nano`) to generate AI agent conversation content. Both Agent A and Agent B are instances of this AI model with system prompts constraining responses to one short sentence.
- **metrics/** — A singleton collector tracking connections, handshakes, packets sent/received, bytes transferred, encrypted messages, replay attacks blocked, rekeys, pings/pongs, and handshake timing.

### 2. Monitor Server (`monitor/`)

- **server.py** — A Flask + Flask-SocketIO server running on port 5000. It receives protocol events from the backend and broadcasts them to all connected dashboard clients via WebSocket using the `protocol_event` channel.
- **events.py** — A helper module providing the `protocol_event()` function that every protocol handler calls to report events. It formats the event data and sends it to the Socket.IO server for broadcasting.

### 3. React Dashboard (`dashboard/`)

- **App.jsx** — Root component rendering the `DashboardLayout`.
- **pages/Dashboard.jsx** — Main page composing all dashboard components into a unified view.
- **hooks/useProtocol.js** — Custom React hook that manages the Socket.IO connection, processes incoming `protocol_event` messages, and maintains state for logs, handshake progress, encryption viewer data, agent statuses, and metrics.
- **services/socket.js** — Socket.IO client configuration connecting to `localhost:5000`.
- **components/protocol/PacketFlow.jsx** — Animated visualization of packets flowing between Agent A and Agent B.
- **components/protocol/HandshakeTimeline.jsx** — Visual step-by-step handshake progress tracker.
- **components/protocol/EncryptionViewer.jsx** — Shows the encryption pipeline: Plaintext -> AES-256-GCM Encrypt -> Ciphertext -> Decrypt -> Recovered.
- **components/protocol/LiveLog.jsx** — Color-coded, searchable, auto-scrolling console of all protocol events.
- **components/cards/AgentCard.jsx** — Status cards for each AI agent.
- **components/cards/MetricCards.jsx** — Metric summary cards (packets, encrypted, rekeys, resumes).
- **components/layout/DashboardLayout.jsx** — Sidebar + main content layout structure.

---

## User Data Flow

### Flow 1: Connection Establishment (QUIC Transport)

The server starts listening on UDP port 4433 using `aioquic` and loads self-signed TLS certificates from the `certs/` directory. The client initiates a QUIC connection to `127.0.0.1:4433`. Both sides create an `AgentProtocol` instance (a subclass of `QuicConnectionProtocol`) and open a bidirectional stream that provides a reader and writer pair for sending and receiving packets.

### Flow 2: Packet Framing

Every message exchanged between client and server is framed with a 4-byte big-endian length prefix. Each packet contains a 24-byte binary header consisting of protocol version, message type, flags, reserved bytes, session ID (UUID), sequence number, and payload length. The payload itself is a JSON-serialized protocol message with binary data (keys, ciphertexts, nonces) encoded as base64 strings.

### Flow 3: Post-Quantum Key Exchange Handshake

The handshake begins with the client sending a HELLO message containing its peer ID, name, and protocol version. The server receives this and responds with a KYBER_PUBLIC_KEY message containing an ML-KEM-768 public key generated by the `pqcrypto` library. The client then performs key encapsulation — it generates a ciphertext and a shared secret from the server's public key. The client derives AES send and receive keys from the shared secret using HKDF-SHA384 and sends the KYBER_CIPHERTEXT message to the server. The server decapsulates the ciphertext to recover the same shared secret, derives its own AES keys via HKDF, and responds with a KEY_CONFIRM message. Both sides now have matching AES-256-GCM keys and the session transitions to the ESTABLISHED state. The client saves session information to `session_cache.json` for potential future resumption.

### Flow 4: Encrypted AI Conversation

Once the session is established, the client generates Agent A's first message using the OpenAI API (`gpt-4.1-nano`). The plaintext message is encrypted with AES-256-GCM using the `CryptoEngine.encrypt()` method and sent as a DATA packet. The server receives the DATA packet, decrypts it using `CryptoEngine.decrypt()`, feeds the recovered plaintext to Agent B via the OpenAI API, encrypts Agent B's reply, and sends it back as a DATA packet. The client decrypts the reply, feeds it to Agent A for a response, encrypts the new reply, and sends it back. This exchange loop continues for a maximum of 5 message rounds.

### Flow 5: Security Mechanisms During Communication

Replay protection is enforced by a `ReplayWindow` that maintains a sliding window of 64 sequence numbers. Any packet with a duplicate or out-of-range sequence number is rejected. Forward secrecy is implemented by the `ForwardSecrecy` class which monitors message counts and triggers a full re-handshake (fresh ML-KEM key exchange) after every 10 messages. Key rotation is handled by the `KeyRotation` class which re-derives AES keys from the existing shared secret using HKDF with an incremented version label, providing additional cryptographic agility without a full re-handshake. A heartbeat mechanism sends PING messages every 5 seconds from the client, to which the server responds with PONG, allowing round-trip time measurement.

### Flow 6: Session Resumption

When a client disconnects and reconnects, it checks for a cached session in `session_cache.json`. If a valid cache exists, the client sends a RESUME message instead of a HELLO. The server looks up the corresponding `SessionTicket` in its `SessionStore`, validates the ticket's expiry (TTL of 1 hour), and if valid, restores the session with its existing cryptographic state, skipping the full handshake. This reduces latency for repeated connections between the same agents.

### Flow 7: Monitoring and Dashboard Visualization

Every protocol handler calls `protocol_event()` from `monitor/events.py` when processing a packet. This function formats the event data (event type, source, message, and extra fields) and sends it to the Flask-SocketIO server. The server broadcasts the event to all connected clients via the `protocol_event` WebSocket channel. On the React dashboard, the `useProtocol` hook listens for these events and updates multiple state variables simultaneously: the live log feed, the handshake timeline progress, the encryption viewer (showing plaintext, ciphertext, and decrypted content), agent status cards, and metric counters. The dashboard components re-render in real time as new events arrive, providing a live visualization of the entire protocol operation.

---

## Data Flow Diagram (Text)

```
User starts Client and Server
         |
         v
Server listens on UDP 4433 (QUIC)
Client connects to localhost:4433
         |
         v
Client sends HELLO  --->  Server receives HELLO
                          Server generates ML-KEM-768 keypair
Server sends KYBER_PUBLIC_KEY  <---  Client receives public key
         |
         v
Client performs encapsulation (ciphertext + shared secret)
Client derives AES keys via HKDF-SHA384
Client sends KYBER_CIPHERTEXT  --->  Server receives ciphertext
         |
         v
Server decapsulates (recovers shared secret)
Server derives AES keys via HKDF-SHA384
Server sends KEY_CONFIRM  <---  Client receives confirmation
         |
         v
SESSION ESTABLISHED
Client saves session cache to disk
         |
         v
Client generates Agent A message (OpenAI API)
Client encrypts message (AES-256-GCM)
Client sends DATA packet  --->  Server receives DATA
         |
         v
Server decrypts message (AES-256-GCM)
Server generates Agent B reply (OpenAI API)
Server encrypts reply (AES-256-GCM)
Server sends DATA packet  <---  Client receives DATA
         |
         v
[Repeat for up to 5 message exchanges]
         |
         v
Every 10 messages: Forward Secrecy triggers REHANDSHAKE
Every 5 seconds: Client sends PING, Server responds PONG
         |
         v
All handlers emit protocol_event() to Monitor Server
Monitor Server broadcasts via Socket.IO WebSocket
         |
         v
React Dashboard receives events
useProtocol hook updates state
Dashboard renders: LiveLog, HandshakeTimeline, PacketFlow,
                   EncryptionViewer, MetricCards, AgentCards
```

---

## Key Configuration

| Parameter | Value | Location |
|---|---|---|
| QUIC Host | `0.0.0.0` / `localhost` | `agent/config.py`, `transport/server.py` |
| QUIC Port | `4433` (UDP) | `agent/config.py`, `transport/server.py` |
| Protocol Version | `1` | `agent/config.py`, `protocol/constants.py` |
| TLS Certs | `certs/cert.pem`, `certs/key.pem` | `transport/server.py` |
| OpenAI Model | `gpt-4.1-nano` | `agent/ai/model.py` |
| Monitor Port | `5000` (HTTP/WS) | `monitor/server.py` |
| Replay Window | 64 packets | `agent/security/replay.py` |
| Forward Secrecy | Every 10 messages | `agent/security/forward_secrecy.py` |
| Key Rotation | Every 10 messages | `agent/security/rotation.py` |
| Session Ticket TTL | 3600 seconds (1 hour) | `agent/session/ticket.py` |
| Max AI Messages | 5 exchanges | `agent/transport/client.py` |
| Heartbeat Interval | 5 seconds | `agent/transport/client.py` |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Transport | QUIC over UDP via `aioquic` |
| Post-Quantum KEM | ML-KEM-768 (CRYSTALS-Kyber) via `pqcrypto` |
| Symmetric Encryption | AES-256-GCM via `cryptography` |
| Key Derivation | HKDF-SHA384 via `cryptography` |
| AI Model | OpenAI GPT-4.1-nano |
| Async Runtime | Python `asyncio` |
| Monitor Server | Flask + Flask-SocketIO |
| Frontend | React 19 + Vite 8 |
| Styling | Tailwind CSS 4 + Radix UI (shadcn/ui) |
| Animations | Framer Motion |
| Charts | Recharts |
| Flow Visualization | React Flow |
| Real-time Data | Socket.IO client |
