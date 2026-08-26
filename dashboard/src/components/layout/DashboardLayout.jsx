import Header from "./Header";
import Sidebar from "./Sidebar";

export default function DashboardLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">

      <Header />

      <div className="flex">

        <Sidebar />

        <main className="flex-1 overflow-y-auto p-8">

          {children}

        </main>

      </div>

    </div>
  );
}
