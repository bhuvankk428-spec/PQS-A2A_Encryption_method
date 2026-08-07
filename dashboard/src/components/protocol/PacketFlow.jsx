import AgentNode from "./AgentNode";
import PacketAnimation from "./PacketAnimation";

export default function PacketFlow() {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-8">

      <h2 className="mb-10 text-2xl font-semibold text-white">
        Live Packet Flow
      </h2>

      <div className="grid grid-cols-[300px_1fr_300px] items-center gap-8">

        <AgentNode
          name="Agent A"
          status="online"
          session="fe14767f..."
        />

        <PacketAnimation
          active={true}
        />

        <AgentNode
          name="Agent B"
          status="online"
          session="fe14767f..."
        />

      </div>

    </div>
  );
}