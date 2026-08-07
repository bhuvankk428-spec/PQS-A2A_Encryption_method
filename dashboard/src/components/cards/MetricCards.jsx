import { TrendingUp } from "lucide-react";

export default function MetricCards({
  title,
  value,
  unit,
  icon: Icon = TrendingUp,
  color = "text-blue-400",
}) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 shadow-sm">

      <div className="flex items-center justify-between">

        <span className="text-sm text-slate-400">
          {title}
        </span>

        <Icon className={`h-5 w-5 ${color}`} />

      </div>

      <div className="mt-4 flex items-end gap-2">

        <h2 className="text-3xl font-bold text-white">
          {value}
        </h2>

        {unit && (
          <span className="pb-1 text-slate-500">
            {unit}
          </span>
        )}

      </div>

    </div>
  );
}