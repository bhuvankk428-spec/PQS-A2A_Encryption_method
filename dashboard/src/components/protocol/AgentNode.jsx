import StatusBadge from "../cards/StatusBadge";
import { Cpu } from "lucide-react";

export default function AgentNode({
  name,
  status = "online",
  session,
}) {
  return (
    <div className="w-72 rounded-2xl border border-slate-800 bg-slate-900 p-6">

      <div className="flex items-center gap-4">

        <div className="rounded-xl bg-blue-600 p-3">
          <Cpu className="text-white" size={28} />
        </div>

        <div>

          <h2 className="text-xl font-semibold text-white">
            {name}
          </h2>

          <StatusBadge
            status={status}
            label={status}
          />

        </div>

      </div>

      <div className="mt-6">

        <p className="text-xs text-slate-500">
          Session
        </p>

        <p className="mt-1 break-all font-mono text-sm text-slate-300">
          {session}
        </p>

      </div>

    </div>
  );
}