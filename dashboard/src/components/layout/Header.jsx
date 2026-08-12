import { ShieldCheck } from "lucide-react";

export default function Header({ connected }) {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950 px-6 flex items-center justify-between">

      <div className="flex items-center gap-3">

        <div className="rounded-lg bg-blue-600 p-2">
          <ShieldCheck className="h-6 w-6 text-white" />
        </div>

        <div>
          <h1 className="text-xl font-semibold text-white">
            Quantum Secure AI Agent Monitor
          </h1>

          <p className="text-sm text-slate-400">
            ML-KEM • QUIC • AES-256 • Session Resume
          </p>
        </div>

      </div>

      <div className="flex items-center gap-3">

        <span
          className={`h-3 w-3 rounded-full ${
            connected
              ? "bg-green-500 animate-pulse"
              : "bg-red-500"
          }`}
        ></span>

        <span className="text-sm text-slate-300">
          {connected ? "Backend Connected" : "Backend Disconnected"}
        </span>

      </div>

    </header>
  );
}