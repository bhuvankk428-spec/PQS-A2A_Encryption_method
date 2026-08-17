import { Play, Loader2, CheckCircle2 } from "lucide-react";

export default function StartButton({
  startBackend,
  backendStatus = "idle",
  connected = false,
}) {
  const isRunning = backendStatus === "started" || backendStatus === "already_running";
  const isFinished = backendStatus === "finished";

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6">

      <div className="flex items-center justify-between">

        <div>
          <h2 className="text-xl font-semibold text-white">
            Backend Control
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Start the QUIC server and client to begin the secure protocol flow
          </p>
        </div>

        <button
          onClick={startBackend}
          disabled={!connected || isRunning}
          className={`
            flex items-center gap-3 rounded-xl px-8 py-4 text-lg font-semibold transition
            ${
              isRunning
                ? "cursor-not-allowed bg-slate-800 text-slate-500"
                : isFinished
                  ? "bg-green-600 text-white hover:bg-green-500"
                  : "bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600"
            }
          `}
        >
          {isRunning ? (
            <>
              <Loader2 size={22} className="animate-spin" />
              Running...
            </>
          ) : isFinished ? (
            <>
              <CheckCircle2 size={22} />
              Finished - Click to Restart
            </>
          ) : (
            <>
              <Play size={22} />
              Start Backend
            </>
          )}

        </button>

      </div>

      {isRunning && (
        <div className="mt-4 flex items-center gap-2 text-sm text-slate-400">
          <Loader2 size={14} className="animate-spin text-blue-400" />
          QUIC server and client are running. Monitoring protocol events...
        </div>
      )}

      {!connected && (
        <div className="mt-4 text-sm text-red-400">
          Backend monitor not connected. Make sure the server is running.
        </div>
      )}

    </div>
  );
}
