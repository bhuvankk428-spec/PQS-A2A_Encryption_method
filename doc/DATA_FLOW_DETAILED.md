# Quantum-Secure AI-to-AI Data Flow — Complete Deep Dive

This document explains **exactly** how a message travels from Agent A's AI brain to
Agent B's AI brain and back — layer by layer, byte by byte — including all encoding,
decoding, encryption, the ML-KEM handshake, and how QUIC works underneath.

All file references are relative to the project root `D:\major_project`.

---

## Table of Contents

1. [Master Block Diagram](#1-master-block-diagram)
2. [The Stack — Who Does What](#2-the-stack--who-does-what)
3. [QUIC From Scratch](#3-quic-from-scratch)
4. [Wire Format — Encoding & Decoding](#4-wire-format--encoding--decoding)
   - 4.1 Frame Layer (length prefix)
   - 4.2 Packet Header (28-byte binary header)
   - 4.3 Payload Encodings per Message Type
5. [The Post-Quantum Handshake — Step by Step](#5-the-post-quantum-handshake--step-by-step)
   - 5.1 ML-KEM-768 Explained
   - 5.2 HKDF Key Derivation
   - 5.3 Handshake Sequence Diagram
6. [Secure Data Flow — AI-to-AI Message Lifecycle](#6-secure-data-flow--ai-to-ai-message-lifecycle)
   - 6.1 Encryption Path (Agent A sends)
   - 6.2 Decryption Path (Agent B receives)
   - 6.3 Full Round-Trip Diagram
7. [Security Subsystems](#7-security-subsystems)
   - 7.1 Replay Protection
   - 7.2 Key Rotation
   - 7.3 Forward Secrecy (full re-handshake)
   - 7.4 Session Resume
8. [Dashboard Event Relay](#8-dashboard-event-relay)

---

## 1. Master Block Diagram

```
+------------------------------------------------------------------------------------------!
|                              PROCESS 2: AGENT A (client)                                  |
|                                                                                           |
|   +------------------+    +-------------+    +---------------+    +--------------------+  |
|   |  AIModel         |    | CryptoEngine|    | Packet        |    | framing.py         |  |
|   |  (gpt-4.1-nano)  |--->| AES-256-GCM |--->| encode()      |--->| 4-byte len prefix  |  |
|   |  "Say hello..."  |    | nonce||ct   |    | 28-byte header|    | writer.write()     |  |
|   +------------------+    +------+------+    +-------+-------+    +---------+----------+  |
|                                      ^              ^                    |                 |
|                                      |              |                    v                 |
|                            +---------+------+  +----+-----------+  +-------------------+  |
|                            | CryptoContext  |  | ProtocolEngine |  | aioquic           |  |
|                            | send/receive   |  | handler map    |  | QuicConnection    |  |
|                            | keys, nonces   |  | HELLO/DATA/... |  | stream reader     |  |
|                            +----------------+  +----------------+  | /writer           |  |
|                                                                    +---------+---------+  |
+-------------------------------------------------------------------------------------------------+
                                                                             |
                                                        TLS 1.3 + QUIC over UDP :4433
                                                        (encrypted transport tunnel)
                                                                             |
+-------------------------------------------------------------------------------------------------+
|                              PROCESS 3: AGENT B (server)                                        |
|                                                                           |                     |
|                                                                   +-------v---------+           |
|                                                                   | aioquic serve() |           |
|                                                                   | stream_handler  |           |
|                                                                   +-------+---------+           |
|                                                                           |                     |
|            +--------------------+    +---------------+    +---------------v-----------+         |
|            | ReplayWindow       |--->| SessionManager|--->| receive_packet()          |         |
|            | seq >= high-64?    |    | get_or_create |    | Packet.decode()           |         |
|            +--------------------+    +-------+-------+    +---------------+-----------+         |
|                                              |                            |                     |
|                                              v                            v                     |
|                                    +-----------------+          +-----------------+             |
|                                    | ProtocolEngine  |--------->| Handler (per    |             |
|                                    | .process()      |          | message type)   |             |
|                                    +-----------------+          +--------+--------+             |
|                                                                          |                     |
|                                                     +--------------------+------------+        |
|                                                     v                    v            v        |
|                                            +----------------+   +-------------+  +---------+   |
|                                            | CryptoEngine   |   | AIModel     |  | monitor |   |
|                                            | decrypt/encrypt|   | Agent B LLM |  | events  |   |
|                                            +----------------+   +-------------+  +----+----+   |
|                                                                                      |         |
+--------------------------------------------------------------------------------------|---------
                                                                                        |
                        HTTP POST /api/emit (localhost:5000)                             v
                                                                        +------------------------+
                                                                        | PROCESS 1: MONITOR     |
                                                                        | Flask-SocketIO :5000   |
                                                                        | socketio.emit(...)     |
                                                                        +-----------+------------+
                                                                                    |
                                                                        WebSocket "protocol_event"
                                                                                    v
                                                                        +------------------------+
                                                                        | PROCESS 4: DASHBOARD   |
                                                                        | React + Socket.IO      |
                                                                        | LiveLog / Metrics      |
                                                                        +------------------------+
```

Four separate OS processes run simultaneously:

| Process | Command | Port | Role |
|---|---|---|---|
| Monitor Server | `python -m monitor.server` | TCP 5000 | Relays protocol events to dashboard |
| Agent B (server) | `python -m agent.transport.server` | UDP 4433 | QUIC server, responds to handshake |
| Agent A (client) | `python -m agent.transport.client` | — | QUIC client, initiates conversation |
| Dashboard | `cd dashboard && npm run dev` | TCP 5173 | Live visualization |

---

## 2. The Stack — Who Does What

```
+-------------------------------------------------------------+
| Layer 6 | AIModel          | generates reply text (OpenAI)  |
| Layer 5 | CryptoEngine     | AES-256-GCM encrypt/decrypt    |
| Layer 4 | Packet + Payload | binary header + JSON/raw body  |
| Layer 3 | framing.py       | 4-byte length-prefix frames    |
| Layer 2 | aioquic streams  | reliable ordered byte streams  |
| Layer 1 | QUIC + TLS 1.3   | encrypted UDP transport        |
| Layer 0 | IP / UDP         | OS network stack               |
+-------------------------------------------------------------+
```

Each layer only talks to its neighbors. A sentence like *"Hello Agent B!"*
passes down through every layer on the way out, and up through every layer
on the way in.

---

## 3. QUIC From Scratch

### 3.1 What QUIC is

QUIC is a modern transport protocol created by Google and standardized by the IETF
(RFC 9000). It replaces TCP+TLS with a **single protocol running over UDP** that has
TLS 1.3 encryption built into the transport itself.

Traditional stack vs QUIC stack:

```
TCP world (old):                QUIC world (this project):

+------------------+            +------------------+
| HTTP / your app  |            | SPQ-A2A protocol |
+------------------+            +------------------+
| TLS (library)    |            |   QUIC           |  <-- TLS 1.3 built-in
+------------------+            +------------------+
| TCP (OS kernel)  |            |   UDP            |
+------------------+            +------------------+
| IP               |            |   IP             |
+------------------+            +------------------+
```

Key properties of QUIC used by this project:

1. **Runs over UDP** — no kernel TCP state machine; everything is done in userspace
   by the `aioquic` library.
2. **TLS 1.3 is mandatory and integrated** — the crypto handshake of the transport
   happens inside QUIC packets themselves, not in a separate layer. Even before our
   own ML-KEM handshake runs, the two agents already share an encrypted, authenticated
   channel.
3. **Streams, not sockets** — one QUIC connection can carry many independent
   *streams*. Each stream is a reliable, ordered byte pipe (like a TCP connection)
   but without head-of-line blocking between streams. This project opens exactly one
   stream per agent session and uses it as a bidirectional pipe.
4. **Connection IDs** — connections survive IP address changes because they are
   identified by a Connection ID, not by the 4-tuple (src ip, src port, dst ip, dst port).

### 3.2 How this project bootstraps QUIC

Server side (`agent/transport/server.py:114`):

```python
configuration = QuicConfiguration(is_client=False)
configuration.load_cert_chain("certs/cert.pem", "certs/key.pem")   # TLS identity

await serve(
    host="0.0.0.0",
    port=4433,                      # UDP socket opened here
    configuration=configuration,
    create_protocol=AgentProtocol,  # QuicConnectionProtocol subclass
    stream_handler=stream_handler,  # called for EVERY incoming stream
)
await asyncio.Future()              # run forever
```

Client side (`agent/transport/client.py:52`):

```python
configuration = QuicConfiguration(is_client=True)
configuration.verify_mode = ssl.CERT_NONE           # trust self-signed cert (dev only)

async with connect(
    "127.0.0.1", 4433,
    configuration=configuration,
    create_protocol=AgentProtocol,
) as protocol:
    reader, writer = await protocol.create_stream() # open 1 bidirectional stream
```

What happens internally when `connect(...)` runs:

```
CLIENT                                          SERVER
  |                                               |
  |  UDP Initial packet (contains TLS ClientHello |
  |  + QUIC connection id + version negotiation)  |
  |---------------------------------------------->|
  |                                               |
  |  UDP packet: TLS ServerHello, cert chain,     |
  |  Finished  (all inside QUIC frames)           |
  |<----------------------------------------------|
  |                                               |
  |  UDP packet: client Finished                  |
  |---------------------------------------------->|
  |                                               |
  |=== TLS 1.3 keys derived on both sides ======= |  <-- transport now encrypted
  |                                               |
  | STREAM frame (stream id 0, offset 0):         |
  |  our first framed application packet          |
  |---------------------------------------------->|
```

Note: this whole exchange is **one or two UDP round trips** (vs TCP's 1 RTT for the
handshake + 1 more RTT inside TLS). After it completes, `connection_made()` fires in
`AgentProtocol` (`agent/transport/protocol.py`) printing `[QUIC] Connection Established`,
and `create_stream()` gives us `(reader, writer)` — asyncio objects that look exactly
like TCP streams but are carried inside QUIC packets over UDP.

From this point upward, neither agent knows or cares about UDP, packets, or TLS.
They just read/write bytes on `reader`/`writer`.

---

## 4. Wire Format — Encoding & Decoding

Three nested layers of structure are added on top of the raw QUIC stream:

```
QUIC stream bytes:
+----------+-------------------------------------+
| 4 bytes  |        N bytes                      |
| length N |   one complete application Packet   |
+----------+-------------------------------------+
     ^                  ^
     |                  |
  framing layer     protocol layer
                     (header + payload)
```

### 4.1 Frame Layer — `agent/transport/framing.py`

A QUIC stream is just an endless byte pipe with no message boundaries, so we add a
**4-byte big-endian length prefix** to every message (`!I` = network byte order,
unsigned 32-bit int):

Sending (`send_packet`, framing.py:9):

```python
data   = packet.encode()               # serialize the Packet object -> bytes
header = struct.pack("!I", len(data))  # e.g. b"\x00\x00\x00\x9c" for 156 bytes
writer.write(header + data)            # one write = one frame
await writer.drain()                   # flush to QUIC
```

Receiving (`receive_packet`, framing.py:28):

```python
header        = await reader.readexactly(4)      # blocks until exactly 4 bytes arrive
packet_length = struct.unpack("!I", header)[0]   # 156
packet        = await reader.readexactly(packet_length)  # blocks until body arrives
```

`readexactly` guarantees a frame is never half-read even if QUIC delivers the bytes
split across multiple internal packets.

### 4.2 Packet Header — `agent/protocol/packet.py`

Every frame contains one `Packet`. Its fixed-size binary header uses
`HEADER_FORMAT = "!BBBB16sII"` — exactly **28 bytes**:

```
Offset  Size  Field           Notes
------  ----  --------------- ---------------------------------------------
0       1     version         PROTOCOL_VERSION = 1, reject if different
1       1     packet_type     MessageType enum value (see below)
2       1     flags           FLAG_ENCRYPTED etc. (currently 0)
3       1     reserved        always 0 (future use)
4       16    session_id      UUID as raw 16 bytes (!)
20      4     sequence        monotonically increasing per sender
24      4     payload_length  how many payload bytes follow the header
```

Encoding (`Packet.encode`, packet.py:28):

```python
header = struct.pack(
    "!BBBB16sII",
    self.version,          # 1
    self.packet_type,      # e.g. 20 (DATA)
    self.flags,            # 0
    self.reserved,         # 0
    self.session_id.bytes, # uuid -> 16 raw bytes
    self.sequence,         # e.g. 3
    len(self.payload),     # e.g. 61
)
return header + self.payload
```

Decoding (`Packet.decode`, packet.py:50) mirrors it with three safety checks:
version must equal 1, `payload_length >= 0`, and `HEADER_SIZE + payload_length`
must not exceed the received bytes ("Packet truncated").

Message types (`agent/protocol/messages.py`):

```
Handshake :  HELLO=1  HELLO_ACK=2  CLIENT_READY=3  SERVER_READY=4
Key exch  :  KYBER_PUBLIC_KEY=10  KYBER_CIPHERTEXT=11  KEY_CONFIRM=12
Data      :  DATA=20
Session   :  REKEY=21  RESUME=22  CLOSE=23
Heartbeat :  PING=40  PONG=41
Errors    :  REHANDSHAKE=50  ERROR=255
```

### 4.3 Payload Encodings per Message Type

Payloads live in `agent/protocol/payloads/`. Two encodings are used:

**JSON payloads** (control messages — human-inspectable, easy to extend):

| Type | Fields | Example on the wire |
|---|---|---|
| HELLO | peer_id, name, version | `{"peer_id":"a1b2...","name":"Agent-A","version":"1.0"}` |
| KYBER_PUBLIC_KEY | peer_id, public_key | base64 string of the 1184-byte KEM key |
| KYBER_CIPHERTEXT | ciphertext | base64 string of the 1088-byte KEM ciphertext |
| KEY_CONFIRM | success | `{"success": true}` |
| RESUME | session_id | cached session's UUID string |

Binary payloads (raw bytes, no JSON overhead):

| Type | Layout | Size |
|---|---|---|
| DATA (encrypted) | `nonce(12) \|\| AES-GCM ciphertext+tag` | 12 + msg_len + 16 |
| PING / PONG | empty or timestamp JSON | ~0-30 bytes |

Base64 conversion for Kyber blobs (`kyber_public_key.py:26`):

```python
json.dumps({
    "peer_id": ...,
    "public_key": base64.b64encode(self.public_key).decode()
}).encode()
```

So a KYBER_PUBLIC_KEY frame is roughly:

```
[4B len=~1600][28B header][{"peer_id":"..","public_key":"<1579 base64 chars>"}]
```

---

## 5. The Post-Quantum Handshake — Step by Step

Before any AI message can be sent, the agents must agree on symmetric AES keys.
This happens over 4 application-level packets riding on top of the already-encrypted
QUIC connection (defense in depth: transport is encrypted by TLS 1.3, AND the
application adds its own post-quantum layer).

### 5.1 ML-KEM-768 Explained

ML-KEM-768 (FIPS 203, formerly CRYSTALS-Kyber) is a **post-quantum Key Encapsulation
Mechanism**. Instead of Diffie-Hellman's "both compute the same number" trick, KEMs
use encapsulate/decapsulate:

```
SERVER (Agent B)                          CLIENT (Agent A)
generate_keypair()
  -> pk  (1184 bytes)  "public lock"
  -> sk  (2400 bytes)  "private key"       receives pk
                                                    |
                                           encapsulate(pk)
                                             -> ct (1088 bytes) "sealed box"
                                             -> ss (32 bytes)   shared secret
                                                    |
                                           derives AES keys from ss
                                           (never needs sk!)
                                           sends ct back
  receives ct
  decapsulate(ct, sk)
    -> ss (32 bytes)   SAME shared secret
  derives same AES keys
```

Why quantum-safe? An attacker recording today's traffic gets `pk` and `ct`.
With a future quantum computer, breaking lattice problems to recover `ss` from
`(pk, ct)` is computationally infeasible — unlike classical DH/ECDH which Shor's
algorithm destroys. Code: `agent/crypto/ml_kem.py` wrapping `pqcrypto.kem.ml_kem_768`.

### 5.2 HKDF Key Derivation

Both sides feed the 32-byte shared secret into HKDF-SHA384
(`agent/crypto/hkdf.py`):

```python
HKDF(algorithm=SHA384(), length=64,
     salt=None, info=b"SPQ-A2A Session Keys v{version}").derive(shared_secret)

key_material (64 bytes):
  send_key   = key_material[:32]   # first 32 bytes
  receive_key= key_material[32:]   # last 32 bytes
```

Direction split prevents reflection attacks — what you encrypt with is never what
you decrypt with:

```
CLIENT: send_key=key1, receive_key=key2
SERVER: send_key=key2, receive_key=key1
```

The `info` string binds keys to a version number. Changing `v1` -> `v2` produces
completely different AES keys from the same secret (used for rekeying).

### 5.3 Handshake Sequence Diagram

```
Agent A (client)                                     Agent B (server)
      |                                                      |
      | 1. HELLO                                             |
      |  type=1, seq=1                                       |
      |  payload = {"peer_id","name","version"} JSON          |
      |----------------------------------------------------->|
      |                                       HelloHandler    |
      |                                       generate fresh  |
      |                                       ML-KEM keypair  |
      |                                       state=HELLO_RECEIVED
      | 2. KYBER_PUBLIC_KEY                                  |
      |  type=10, seq=1                                      |
      |  payload={"public_key": base64(1184 B)}               |
      |<-----------------------------------------------------|
   KyberPublicKeyHandler                                     |
   encapsulate(pk) -> ct(1088 B), ss(32 B)                   |
   load_shared_secret(ss, is_client=True)                    |
     -> AES keys ready (can already encrypt!)                |
   state stays HELLO_SENT                                    |
      | 3. KYBER_CIPHERTEXT                                  |
      |  type=11, seq=2                                      |
      |  payload={"ciphertext": base64(1088 B)}               |
      |----------------------------------------------------->|
      |                                     KyberCiphertextHandler
      |                                     kem.sk = stored sk
      |                                     decapsulate(ct) -> SAME ss
      |                                     load_shared_secret(ss, is_client=False)
      |                                     state=ESTABLISHED
      |                                     store ticket (resume later)
      | 4. KEY_CONFIRM                                       |
      |  type=12, seq=2, {"success":true}                    |
      |<-----------------------------------------------------|
   KeyConfirmHandler                                         |
   crypto.establish()                                        |
   state=ESTABLISHED                                         |
   cache session (session_cache.json)                        |
      |                                                      |
      |===== POST-QUANTUM SECURE CHANNEL ACTIVE =============|
```

Handler source files:
- `agent/protocol/handlers/hello.py` — generates Keypair, replies with pk
- `agent/protocol/handlers/kyber_public_key.py` — encapsulates, derives keys, sends ct
- `agent/protocol/handlers/kyber_ciphertext.py` — decapsulates, marks ESTABLISHED, sends confirm
- `agent/protocol/handlers/key_confirm.py` — client confirms + caches ticket

Every step also fires `protocol_event(...)` so the dashboard timeline lights up
(HELLO -> KYBER_PUBLIC_KEY -> KYBER_CIPHERTEXT -> KEY_CONFIRM).

---

## 6. Secure Data Flow — AI-to-AI Message Lifecycle

Now the actual question: **how does one AI's sentence reach the other AI?**

### 6.1 Encryption Path (Agent A sends, `agent/transport/client.py:293`)

Suppose OpenAI returns `"Hello Agent B, our keys are quantum-proof!"`.

```
Step 1. AI text
   "Hello Agent B, our keys are quantum-proof!"
        |
        | reply.encode()                       <- UTF-8 encoding (str -> bytes)
        v
Step 2. Plaintext bytes (44 bytes)

Step 3. Nonce generation (CryptoContext.next_nonce, context.py:28)
   nonce_counter starts at 0, increments per message
   nonce = counter.to_bytes(12, "big")        e.g. b"\x00...\x03" (counter=3)
   NEVER reused with the same key -> GCM safety requirement

Step 4. AES-256-GCM encrypt (Cipher.encrypt, cipher.py:10)
   AESGCM(send_key).encrypt(nonce, plaintext, aad=b"")
   output = ciphertext || 16-byte auth tag   (48+16 = 60 bytes)
   Any tampering -> tag check fails at receiver -> exception -> dropped

Step 5. Wire blob = nonce || ciphertext||tag
   CryptoEngine.encrypt returns nonce + ciphertext   (engine.py:31)
   [12B nonce][60B ct+tag] = 72 bytes

Step 6. Packet assembly (Packet.encode)
   header 28 B  {ver=1, type=20(DATA), flags=0, rsvd=0,
                 session_id=16B, sequence=N, len=72}
   frame   = [4B total_len=100][28B header][72B blob]

Step 7. QUIC delivery (framing.send_packet)
   writer.write(frame); await writer.drain()
   aioquic chops the frame into QUIC STREAM frames,
   encrypts them with TLS 1.3 keys, sends UDP datagrams
```

### 6.2 Decryption Path (Agent B receives, `agent/protocol/handlers/data.py`)

Exact mirror image:

```
UDP datagram arrives on port 4433
        |
aioquic authenticates + decrypts TLS record, reassembles stream order,
feeds bytes to stream_handler's reader
        |
receive_packet(): readexactly(4) -> 100 ; readexactly(100) -> frame
        |
Packet.decode(data):
   unpack "!BBBB16sII" -> type=DATA, session_id, sequence
   payload = data[28:100]
        |
server.py:49  manager.get_or_create(session_id)   <- find/create Session
server.py:56  session.replay.validate(sequence)?  <- replay attack? drop.
        |
ProtocolEngine.process(session, packet)  -> routes by type=20 to DataHandler
        |
CryptoEngine.decrypt(session, payload)   (engine.py:34)
   nonce      = payload[:12]
   ciphertext = payload[12:]
   AESGCM(receive_key).decrypt(nonce, ciphertext)   <- raises if tag invalid
        |
plaintext bytes -> plaintext.decode() (UTF-8 -> str)
        |
"Hello Agent B, our keys are quantum-proof!"
        |
Step: Agent B THINKS (data.py:46)
   agent_b.chat("... You are Agent B ... Agent A said: <text>")
   -> calls OpenAI gpt-4.1-nano, gets one-sentence reply
        |
reply encoded -> CryptoEngine.encrypt (same steps 3-5, own nonce counter)
        |
return Packet(type=DATA, ...)  -> server.py sends it back down the same stream
```

### 6.3 Full Round-Trip Diagram

```
 AGENT A                                                AGENT B
 ========                                               ========
 AIModel.chat() -> "Hello..."                                 
      | UTF-8 encode()                                        
      v                                                        
 plaintext bytes                                              
      | AES-256-GCM encrypt                                   
      |   key = send_key  (from HKDF v1)                      
      |   nonce = counter++ (12 B)                            
      v                                                        
 [nonce|ct|tag]                                               
      | Packet.encode  (+28B header)                          
      | framing.send_packet (+4B len)                         
      v                                                        
 ============== QUIC / UDP :4433 (TLS 1.3 inner encryption) ===>
                                                               receive_packet(-4B)
                                                               Packet.decode(-28B)
                                                               replay.validate(seq)
                                                               CryptoEngine.decrypt
                                                                  key = receive_key
                                                               UTF-8 decode()
                                                               AIModel.chat(text)
                                                                     ... thinks ...
                                                               reply UTF-8 encode
                                                               AES-256-GCM encrypt
                                                                  key = send_key
                                                               [nonce|ct|tag]
 <=============== QUIC / UDP :4433 (same QUIC connection) ======
 framing.receive_packet
 Packet.decode
 replay.validate(seq)
 CryptoEngine.decrypt (receive_key)
 UTF-8 decode -> str
 print + next AI turn...
```

Heartbeats ride the same path: a `heartbeat()` task (`client.py:30`) sends a PING
packet every 5 s; PingHandler answers with PONG. These keep NAT mappings alive and
double as liveness detection.

---

## 7. Security Subsystems

### 7.1 Replay Protection — `agent/security/replay.py`

Every Packet carries a monotonic `sequence` number. The receiver keeps a sliding
window of the highest 64 sequence numbers seen:

```
validate(seq):
  duplicate (already in set)            -> REJECT
  seq < highest_seen - 64 (too old)     -> REJECT
  otherwise                             -> ACCEPT, track it
```

An attacker who copies a valid `[nonce|ciphertext]` frame and replays it verbatim
gets dropped before decryption even runs.

### 7.2 Key Rotation — `agent/security/rotation.py`

After every 10 encrypted messages (`ROTATION_INTERVAL`), both sides re-derive fresh
AES keys from the *same* shared secret but a bumped version tag:

```
v1: HKDF(secret, info="SPQ-A2A Session Keys v1") -> k1,k2
v2: HKDF(secret, info="SPQ-A2A Session Keys v2") -> completely new k1,k2
```

Because HKDF output changes totally with `info`, compromise of one epoch's keys
reveals nothing about another epoch's keys.

### 7.3 Forward Secrecy — Full Re-Handshake (`forward_secrecy.py`, `rehandshake.py`)

Rotation still reuses the original Kyber secret. So after 10 messages the client
runs a **complete second ML-KEM handshake** on the live connection:

```
client: should_rehandshake()? -> yes
        send REHANDSHAKE packet, then a brand-new HELLO
server: HelloHandler sees rehandshaking=True
        generates a FRESH ML-KEM keypair
        ... normal 4-step handshake repeats ...
both:   old shared_secret discarded, counters reset,
        all future DATA uses the new epoch's keys
```

Result: even if an adversary later obtains the current session secret, messages
from earlier epochs remain unreadable (they were protected by long-deleted keys).

### 7.4 Session Resume — `agent/session/*`, `handlers/resume.py`

Full handshakes cost CPU (Kyber keygen + encapsulation). After a successful one:

- **Client** writes `{session_id, shared_secret, key_version}` to
  `session_cache.json` (KeyConfirmHandler).
- **Server** stores a `SessionTicket` in its in-memory `store`.

Next time the client starts, it loads the cache and sends a `RESUME` packet instead
of HELLO. The server finds the ticket, reloads the shared secret, re-derives the
same AES keys, replies `SESSION_RESUME_ACK` — skipping the entire Kyber exchange.
Zero post-quantum work, instant secure session.

---

## 8. Dashboard Event Relay

Handlers do not talk to the dashboard directly — they live in different OS processes
than the Socket.IO server. Instead every interesting moment calls
(`monitor/events.py`):

```
handler -> protocol_event(type, source, msg, **extra)
             |
             | HTTP POST http://localhost:5000/api/emit   (JSON body)
             v
monitor/server.py relay_event() -> socketio.emit("protocol_event", event)
             |
             | WebSocket broadcast
             v
dashboard useProtocol hook -> setLogs / setMetrics / setEncryption
             |
             v
LiveLog | HandshakeTimeline | PacketFlow | MetricCards | AgentCard
```

Event types emitted during one conversation:
`HELLO, KYBER_PUBLIC_KEY, SHARED_SECRET, KYBER_CIPHERTEXT, SESSION_STORE,
KEY_CONFIRM, SESSION_CACHE, DATA, PING/PONG, REKEY, KEY_ROTATION,
REHANDSHAKE, FORWARD_SECRECY, SESSION_RESUME(_ACK)`.

---

## Quick Reference — Byte Accounting for One DATA Message

| Component | Bytes |
|---|---|
| Frame length prefix | 4 |
| Packet header | 28 |
| Nonce | 12 |
| AES-GCM ciphertext (= plaintext length) | n |
| AES-GCM authentication tag | 16 |
| **Total on the QUIC stream** | **60 + n** |

For a 15-word AI sentence (~80 chars): ~140 bytes of application data, wrapped in
TLS 1.3 records (~30 extra bytes of QUIC/TLS overhead per datagram) over UDP.
