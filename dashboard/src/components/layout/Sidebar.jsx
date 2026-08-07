import {
  Activity,
  Shield,
  ArrowLeftRight,
  FileText,
  BarChart3,
  Cpu,
} from "lucide-react";

const menus = [
  {
    icon: Activity,
    title: "Overview",
  },
  {
    icon: ArrowLeftRight,
    title: "Packet Flow",
  },
  {
    icon: Shield,
    title: "Handshake",
  },
  {
    icon: Cpu,
    title: "Encryption",
  },
  {
    icon: BarChart3,
    title: "Metrics",
  },
  {
    icon: FileText,
    title: "Logs",
  },
];

export default function Sidebar() {
  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950">

      <nav className="p-4 space-y-2">

        {menus.map((item) => {

          const Icon = item.icon;

          return (
            <button
              key={item.title}
              className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-slate-300 transition hover:bg-slate-800 hover:text-white"
            >
              <Icon size={18} />

              <span>{item.title}</span>

            </button>
          );
        })}

      </nav>

    </aside>
  );
}