import { useEffect, useRef, useState } from "react";
import socket from "../services/socket";

export function useProtocol() {

    const [logs, setLogs] = useState([]);

    const [metrics, setMetrics] = useState({
        packets: 0,
        encrypted: 0,
        decrypted: 0,
        rekeys: 0,
        resumes: 0,
    });

    const [handshake, setHandshake] = useState("HELLO");

    const [encryption, setEncryption] = useState({
        plaintext: "",
        ciphertext: "",
        decrypted: "",
    });

    const [agentA, setAgentA] = useState({
        status: "online",
        session: "-",
        keyVersion: 1,
    });

    const [agentB, setAgentB] = useState({
        status: "online",
        session: "-",
        keyVersion: 1,
    });

    const rehandshakeInProgress = useRef(false);
    const rehandshakeDone = useRef(false);

    useEffect(() => {

        socket.on("connect", () => {
            console.log("Connected");
        });

        socket.on("protocol_event", (event) => {

            event.time = new Date().toLocaleTimeString();

            setLogs((prev) => [...prev, event]);

            setMetrics((prev) => ({
                ...prev,
                packets: prev.packets + 1,
            }));

            switch (event.type) {

                case "HELLO":
                    if (
                        !rehandshakeInProgress.current
                        && !rehandshakeDone.current
                    ) {
                        setHandshake("HELLO");
                    }
                    break;

                case "KYBER_PUBLIC_KEY":
                    if (
                        !rehandshakeInProgress.current
                        && !rehandshakeDone.current
                    ) {
                        setHandshake("KYBER_PUBLIC_KEY");
                    }
                    break;

                case "KYBER_CIPHERTEXT":
                    if (
                        !rehandshakeInProgress.current
                        && !rehandshakeDone.current
                    ) {
                        setHandshake("KYBER_CIPHERTEXT");
                    }
                    break;

                case "KEY_CONFIRM":
                    if (
                        !rehandshakeInProgress.current
                        && !rehandshakeDone.current
                    ) {
                        setHandshake("KEY_CONFIRM");
                    }
                    break;

                case "DATA":

                    if (
                        !rehandshakeInProgress.current
                        && !rehandshakeDone.current
                    ) {
                        setHandshake("DATA");
                    }

                    setEncryption({
                        plaintext: event.plaintext || "",
                        ciphertext: event.ciphertext || "",
                        decrypted: event.decrypted || event.plaintext || "",
                    });

                    setMetrics((prev) => ({
                        ...prev,
                        encrypted: prev.encrypted + 1,
                        decrypted: prev.decrypted + 1,
                    }));

                    break;

                case "REHANDSHAKE":
                    rehandshakeInProgress.current = true;
                    setHandshake("REHANDSHAKE");
                    break;

                case "FORWARD_SECRECY":
                    rehandshakeInProgress.current = false;
                    rehandshakeDone.current = true;
                    setHandshake("REHANDSHAKE");
                    break;

                case "RESUME":
                case "SESSION_RESUME_ACK":

                    setMetrics((prev) => ({
                        ...prev,
                        resumes: prev.resumes + 1,
                    }));

                    break;

                case "KEY_ROTATION":

                    setMetrics((prev) => ({
                        ...prev,
                        rekeys: prev.rekeys + 1,
                    }));

                    break;

                default:
                    break;
            }

            if (event.session) {

                setAgentA((prev) => ({
                    ...prev,
                    session: event.session,
                }));

                setAgentB((prev) => ({
                    ...prev,
                    session: event.session,
                }));
            }

            if (event.key_version) {

                setAgentA((prev) => ({
                    ...prev,
                    keyVersion: event.key_version,
                }));

                setAgentB((prev) => ({
                    ...prev,
                    keyVersion: event.key_version,
                }));
            }

        });

        return () => {

            socket.off("connect");
            socket.off("protocol_event");

        };

    }, []);

    return {

        logs,

        metrics,

        handshake,

        encryption,

        agentA,

        agentB,

    };
}