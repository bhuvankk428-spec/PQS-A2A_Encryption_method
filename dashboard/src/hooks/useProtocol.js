import { useEffect, useState } from "react";
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