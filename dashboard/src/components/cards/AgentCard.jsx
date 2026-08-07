import StatusBadge from "./StatusBadge";

export default function AgentCard({
  name,
  status,
  session,
  keyVersion,
  packets,
  encrypted,
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">

      <div className="flex items-center justify-between">

        <h2 className="text-xl font-semibold text-white">
          {name}
        </h2>

        <StatusBadge
          status={status}
          label={status}
        />

      </div>

      <div className="mt-6 space-y-3">

        <InfoRow
          label="Session"
          value={session}
        />

        <InfoRow
          label="Key Version"
          value={keyVersion}
        />

        <InfoRow
          label="Packets"
          value={packets}
        />

        <InfoRow
          label="Encrypted"
          value={encrypted}
        />

      </div>

    </div>
  );
}

function InfoRow({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-800 pb-2">

      <span className="text-slate-400">
        {label}
      </span>

      <span className="font-medium text-white">
        {value}
      </span>

    </div>
  );
}