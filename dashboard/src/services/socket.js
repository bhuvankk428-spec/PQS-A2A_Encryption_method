import { io } from "socket.io-client";

const socket = io("http://localhost:5000", {
    transports: ["websocket", "polling"],
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
});

export default socket;
