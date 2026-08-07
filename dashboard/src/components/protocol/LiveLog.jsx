import { useEffect, useRef, useState } from "react";
import {
  Terminal,
  Trash2,
  Search,
} from "lucide-react";

const colors = {
  HELLO: "text-cyan-400",
  KYBER_PUBLIC_KEY: "text-purple-400",
  KYBER_CIPHERTEXT: "text-indigo-400",
  SHARED_SECRET: "text-emerald-400",
  KEY_CONFIRM: "text-green-400",
  DATA: "text-blue-400",
  REHANDSHAKE: "text-orange-400",
  REKEY: "text-yellow-400",
  RESUME: "text-pink-400",
  PING: "text-sky-400",
  PONG: "text-sky-300",
  ERROR: "text-red-500",
};

export default function LiveLog({ logs = [] }) {
  const bottomRef = useRef(null);

  const [search, setSearch] = useState("");

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [logs]);

  const filteredLogs = logs.filter((log) => {
    if (!search) return true;

    return JSON.stringify(log)
      .toLowerCase()
      .includes(search.toLowerCase());
  });

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950">

      {/* Header */}

      <div className="flex items-center justify-between border-b border-slate-800 p-4">

        <div className="flex items-center gap-3">

          <Terminal
            size={20}
            className="text-green-400"
          />

          <h2 className="text-lg font-semibold text-white">
            Live Protocol Console
          </h2>

        </div>

        <button
          className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-800 hover:text-red-400"
        >
          <Trash2 size={18} />
        </button>

      </div>

      {/* Search */}

      <div className="border-b border-slate-800 p-4">

        <div className="flex items-center rounded-lg border border-slate-700 bg-slate-900 px-3">

          <Search
            size={18}
            className="text-slate-500"
          />

          <input
            placeholder="Search logs..."
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
            className="w-full bg-transparent px-3 py-2 text-white outline-none"
          />

        </div>

      </div>

      {/* Logs */}

      <div className="h-[420px] overflow-y-auto p-4 font-mono text-sm">

        {filteredLogs.length === 0 && (

          <div className="text-slate-500">

            Waiting for protocol events...

          </div>

        )}

        {filteredLogs.map((log, index) => (

          <div
            key={index}
            className="mb-3 rounded-lg border border-slate-800 bg-slate-900 p-3"
          >

            <div className="flex items-center justify-between">

              <span
                className={`font-semibold ${
                  colors[log.type] || "text-white"
                }`}
              >
                {log.type}
              </span>

              <span className="text-xs text-slate-500">
                {log.time}
              </span>

            </div>

            <div className="mt-2 text-slate-300">

              {log.message}

            </div>

            {log.plaintext && (

              <div className="mt-2 text-green-400">

                Plaintext: {log.plaintext}

              </div>

            )}

            {log.ciphertext && (

              <div className="mt-2 break-all text-cyan-400">

                Cipher: {log.ciphertext}

              </div>

            )}

          </div>

        ))}

        <div ref={bottomRef} />

      </div>

    </div>
  );
}