
1. QUIC was designed by Google as a modern alternative to TCP. It runs over UDP, encrypts the transport by default, and makes protocol upgrades much easier because it does not depend on operating system changes.

2. QUIC does not tie a connection to a fixed IP address and port combination. Instead, it uses Connection IDs, which means a session can continue even if the network changes, such as when a device switches from Wi-Fi to mobile data.

3. One of QUIC's biggest practical advantages is 0-RTT session resumption. A returning client can start sending data immediately, which is especially useful for A2A systems where agents often exchange many short requests.

4. QUIC supports multiple independent streams inside a single connection. If one packet is lost, the other streams can continue, avoiding the head-of-line blocking problem that affects TCP.

5. Google reported strong real-world results from QUIC deployment, including lower search latency and less YouTube buffering. That shows QUIC is not just academically interesting; it works at massive scale.

6. TLS 1.3 forms the security foundation of this design. It removed many outdated and weak cryptographic options and made forward secrecy a standard part of every secure session.

7. A major strength of TLS 1.3 is that its key exchange layer is modular. That means new algorithms, including post-quantum ones, can be added without redesigning the rest of the protocol.

8. QUIC and TLS 1.3 are closely integrated. QUIC uses the TLS handshake to derive secrets, and then those secrets protect every packet sent over the connection.

9. The main quantum threat is to today's public-key key exchange, especially ECDH. A sufficiently powerful quantum computer could break it using Shor's algorithm.

10. The important point is that not everything in QUIC becomes insecure in a quantum future. The main part that needs replacement is the key exchange, while the symmetric encryption components remain strong.

11. This matters now because of the Harvest Now, Decrypt Later threat. An attacker can record encrypted traffic today and wait until better quantum capabilities arrive to try to decrypt it later.

12. ML-KEM, which comes from CRYSTALS-Kyber, is the post-quantum key encapsulation method selected by NIST. It was standardized as FIPS 203 in August 2024 after years of international evaluation.

13. ML-KEM is considered quantum-resistant because it is built on the hardness of the Module Learning With Errors problem. At present, no efficient classical or quantum attack is known against it.

14. ML-KEM is also practical for deployment. Its key and ciphertext sizes are larger than ECDH, but still small enough to fit within normal TLS and QUIC handshake structures.

15. This is no longer a theoretical technology. ML-KEM and hybrid post-quantum handshakes have already been deployed by major platforms such as Chrome, Cloudflare, AWS, Signal, and Apple ecosystems.

16. Performance measurements are encouraging. In many benchmark studies, ML-KEM adds only a very small handshake delay, often under a couple of milliseconds in normal conditions.

17. QUIC becomes even more attractive when post-quantum cryptography is added. Under lossy network conditions, QUIC-based handshakes tend to perform better than TCP plus TLS because QUIC avoids TCP's transport overheads.

18. The safest transition path is hybrid mode. In a hybrid handshake, a classical algorithm like X25519 and a post-quantum algorithm like ML-KEM-768 are both used together.

19. Hybrid mode is valuable because it reduces migration risk. Even if one algorithm is later weakened, the session remains secure as long as the other one still holds.

20. This hybrid approach is not experimental anymore. Chrome has already used hybrid TLS with X25519 and ML-KEM as a default option for large-scale HTTPS protection.

21. Research such as KyberSlash showed that implementation quality matters just as much as mathematical design. A theoretically secure algorithm can still fail if the code leaks secrets through timing behavior.

22. Because of that, constant-time implementations are essential. Any A2A deployment using ML-KEM must rely on well-audited libraries that are specifically designed to resist side-channel attacks.

23. Frequent key rotation is another practical defense. If an implementation flaw is discovered, shorter-lived key pairs reduce the amount of data exposed.

24. The history of post-quantum cryptography also shows why caution is necessary. SIKE, once seen as a promising candidate, was broken quickly by a classical attack, proving that ongoing review and algorithm diversity are important.

25. The overall conclusion is clear: combining A2A communication with QUIC and replacing classical key exchange with ML-KEM or hybrid ML-KEM creates a transport layer that is faster, more resilient, and better prepared for the quantum era.



| # | Topic | Channel | Link |
|---|---|---|---|
| 1 | Quantum threat & Shor's algorithm | Veritasium | youtu.be/-UrdExQW0cs |
| 2 | Shor's algorithm (short) | minutephysics | youtu.be/lvTqbM5Dq4Q |
| 4 | HTTP 1 vs 2 vs 3 animated | ByteByteGo | youtu.be/UMwQjFzTQXw |
| 5 | QUIC becomes IETF standard | Hussein Nasser | youtu.be/Ky5nTTzMrpE |
| 6 | TLS history & what it does | Computerphile | youtu.be/0TLDTodL7Lc |
| 7 | TLS handshake step by step | Computerphile | youtu.be/86cQJ0MMses |
| 8 | HTTPS & TLS animated | ByteByteGo | youtu.be/j9QmMEWmcfo |
| 9 | Post-quantum cryptography intro | Computerphile | youtu.be/tD-m0BgrCDw |
| 10 | Quantum-safe crypto explained | IBM Technology | youtu.be/HrlCSS-KFYU |
| 11 | NIST PQC standardisation | NIST Official | youtu.be/j_n8R4gAE9Y |
| 12 | Grover's algorithm & AES safety | 3Blue1Brown | youtu.be/lvTqbM5Dq4Q |
| 13 | Hybrid PQC deployment | Cloudflare | youtu.be/LyYtOGj8J5s |
| 14 | Hybrid TLS 1.3 IETF design | USENIX Security | youtu.be/ODQv5tGBVEE |
| 15 | Side-channel attacks explained | Computerphile | youtu.be/PuVMkSjhK-U |
| 16 | Timing attacks on crypto | LiveOverflow | youtu.be/JHRnAXyy-fE |




























