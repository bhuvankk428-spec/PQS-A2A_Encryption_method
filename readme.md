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
Session Close
```

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




PS D:\major_project\agent> cd D:\major_project
>> .\venv\Scripts\Activate.ps1
>> python -m agent.transport.server   










python -m agent.transport.client
