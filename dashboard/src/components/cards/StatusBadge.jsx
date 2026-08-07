const colors = {
  online: "bg-green-500",
  offline: "bg-red-500",
  handshake: "bg-blue-500",
  warning: "bg-yellow-500",
  idle: "bg-slate-500",
};

export default function StatusBadge({
  status = "online",
  label,
}) {
  return (
    <div className="flex items-center gap-2">

      <span
        className={`h-2.5 w-2.5 rounded-full ${
          colors[status] || colors.idle
        }`}
      />

      <span className="text-sm text-slate-300">
        {label}
      </span>

    </div>
  );
}