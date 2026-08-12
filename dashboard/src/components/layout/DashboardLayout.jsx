import Header from "./Header";
import Sidebar from "./Sidebar";

export default function DashboardLayout({
  connected = false,
  children,
}) {
  return (
    <div className="flex h-screen overflow-hidden bg-slate-950 text-white">

      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">

        <Header connected={connected} />

        <main className="flex-1 overflow-y-auto p-6">

          {children}

        </main>

      </div>

    </div>
  );
}