import { useEffect, useState, useCallback } from "react";
import socket from "../services/socket";

export function useProtocol() {

    const [connected, setConnected] = useState(socket.connected);

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

    const [conversation, setConversation] = useState([]);

    const [agentA, setAgentA] = useState({
        status: "offline",
        session: "-",
        keyVersion: 1,
    });

    const [agentB, setAgentB] = useState({
        status: "offline",
        session: "-",
        keyVersion: 1,
    });

    const [backendStatus, setBackendStatus] = useState("idle");

    const startBackend = useCallback(() => {
        socket.emit("start_backend");
    }, []);

    const clearLogs = useCallback(() => {
        setLogs([]);
    }, []);

    useEffect(() => {

        socket.on("connect", () => {
            console.log("Connected to monitor backend");
            setConnected(true);
        });

        socket.on("disconnect", () => {
            console.log("Disconnected from monitor backend");
            setConnected(false);
        });

        socket.on("backend_status", (data) => {
            setBackendStatus(data.status);
        });

        socket.on("protocol_event", (event) => {

            event.time = new Date().toLocaleTimeString();

            setLogs((prev) => [...prev, event]);

            // Raw client console output streamed by the monitor backend.
            if (event.type === "CONSOLE") {
                return;
            }

            setMetrics((prev) => ({
                ...prev,
                packets: prev.packets + 1,
            }));

            // Source identifies which agent emitted the event.
            if (event.source === "CLIENT") {
                setAgentA((prev) => ({ ...prev, status: "online" }));
            } else if (event.source === "SERVER") {
                setAgentB((prev) => ({ ...prev, status: "online" }));
            }

            switch (event.type) {

                case "HELLO":
                    setHandshake("HELLO");
                    break;

                case "KYBER_PUBLIC_KEY":
                    setHandshake("KYBER_PUBLIC_KEY");
                    break;

                case "KYBER_CIPHERTEXT":
                    setHandshake("KYBER_CIPHERTEXT");
                    break;

                case "KEY_CONFIRM":
                    setHandshake("KEY_CONFIRM");
                    break;

                case "DATA":

                    setHandshake("DATA");

                    setEncryption({
                        plaintext: event.plaintext || "",
                        ciphertext: event.ciphertext || "",
                        decrypted: event.plaintext || "",
                    });

                    setMetrics((prev) => ({
                        ...prev,
                        encrypted: prev.encrypted + (event.ciphertext ? 1 : 0),
                        decrypted: prev.decrypted + (event.plaintext ? 1 : 0),
                    }));

                    if (event.source === "CLIENT" && event.plaintext) {
                        const speaker =
                            event.message === "Message from Agent B decrypted"
                                ? "Agent B"
                                : "Agent A";

                        setConversation((prev) => [
                            ...prev,
                            { agent: speaker, text: event.plaintext },
                        ]);
                    }

                    break;

                case "REHANDSHAKE":
                    setHandshake("REHANDSHAKE");
                    break;

                case "RESUME":

                    setMetrics((prev) => ({
                        ...prev,
                        resumes: prev.resumes + 1,
                    }));

                    break;

                case "REKEY":

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

        });

        return () => {

            socket.off("connect");
            socket.off("disconnect");
            socket.off("protocol_event");
            socket.off("backend_status");

        };

    }, []);

    return {

        connected,

        logs,

        metrics,

        handshake,

        encryption,

        conversation,

        agentA,

        agentB,

        backendStatus,

        startBackend,

        clearLogs,

    };
}
