import DashboardLayout from "../components/layout/DashboardLayout";

import PacketFlow from "../components/protocol/PacketFlow";
import HandshakeTimeline from "../components/protocol/HandshakeTimeline";
import EncryptionViewer from "../components/protocol/EncryptionViewer";
import LiveLog from "../components/protocol/LiveLog";

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
    logs,
    metrics,
    handshake,
    encryption,
    agentA,
    agentB,
  } = useProtocol();

  return (

    <DashboardLayout>

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

        <PacketFlow />

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

      {/* ---------------- Logs ---------------- */}

      <div className="mt-8">

        <LiveLog logs={logs} />

      </div>

    </DashboardLayout>

  );
}