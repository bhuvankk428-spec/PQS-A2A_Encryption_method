import { io } from "socket.io-client";

// The monitor backend runs on http://localhost:5000 by default (started by
// agent/transport/server.py). Override with VITE_SOCKET_URL if deploying the
// dashboard separately.
const socket = io(import.meta.env.VITE_SOCKET_URL || "http://localhost:5000", {
  transports: ["websocket"],
});

export default socket;