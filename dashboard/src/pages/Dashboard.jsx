import DashboardLayout from "../components/layout/DashboardLayout";

import PacketFlow from "../components/protocol/PacketFlow";
import HandshakeTimeline from "../components/protocol/HandshakeTimeline";
import EncryptionViewer from "../components/protocol/EncryptionViewer";
import LiveLog from "../components/protocol/LiveLog";
import StartButton from "../components/protocol/StartButton";
import ChatPanel from "../components/protocol/ChatPanel";

import AgentCard from "../components/cards/AgentCard";
import MetricCards from "../components/cards/MetricCards";

import { useProtocol } from "../hooks/useProtocol";

import {
  Activity,
  Shield,
  Lock,
  Timer,
} from "lucide-react";

export default function Dashboard() {

  const {
    connected,
    logs,
    metrics,
    handshake,
    encryption,
    conversation,
    agentA,
    agentB,
    backendStatus,
    startBackend,
    clearLogs,
  } = useProtocol();

  return (

    <DashboardLayout connected={connected}>

      {/* ---------------- Start Button ---------------- */}

      <div className="mb-6">

        <StartButton
          startBackend={startBackend}
          backendStatus={backendStatus}
          connected={connected}
        />

      </div>

      {/* ---------------- Agent Cards ---------------- */}

      <div className="grid grid-cols-2 gap-6">

        <AgentCard
          name="Agent A"
          status={agentA.status}
          session={agentA.session}
          keyVersion={agentA.keyVersion}
          packets={metrics.packets}
          encrypted={metrics.encrypted}
        />

        <AgentCard
          name="Agent B"
          status={agentB.status}
          session={agentB.session}
          keyVersion={agentB.keyVersion}
          packets={metrics.packets}
          encrypted={metrics.decrypted}
        />

      </div>

      {/* ---------------- Metrics ---------------- */}

      <div className="mt-6 grid grid-cols-4 gap-5">

        <MetricCards
          title="Packets"
          value={metrics.packets}
          icon={Activity}
        />

        <MetricCards
          title="Encrypted"
          value={metrics.encrypted}
          icon={Lock}
        />

        <MetricCards
          title="Rekeys"
          value={metrics.rekeys}
          icon={Shield}
        />

        <MetricCards
          title="Resumes"
          value={metrics.resumes}
          icon={Timer}
        />

      </div>

      {/* ---------------- Packet Animation ---------------- */}

      <div className="mt-8">

        <PacketFlow
          agentA={agentA}
          agentB={agentB}
          connecting={connected && logs.length > 0}
        />

      </div>

      {/* ---------------- Timeline + Encryption ---------------- */}

      <div className="mt-8 grid grid-cols-2 gap-6">

        <HandshakeTimeline
          current={handshake}
        />

        <EncryptionViewer
          plaintext={encryption.plaintext}
          ciphertext={encryption.ciphertext}
          decrypted={encryption.decrypted}
        />

      </div>

      {/* ---------------- Conversation + Logs ---------------- */}

      <div className="mt-8 grid grid-cols-2 gap-6">

        <ChatPanel
          conversation={conversation}
          connected={connected}
        />

        <LiveLog logs={logs} onClear={clearLogs} />

      </div>

    </DashboardLayout>

  );
}
